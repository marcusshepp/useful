import requests
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

organization = 'Legislative'
project = 'LegBone'
team = 'LegBone Team'
token = os.getenv('AZURE_TOKEN')
encoded_token = base64.b64encode(f':{token}'.encode()).decode()
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_token}'
}

current_sprint = 'Sprint 70'
sprint_range_start = 66
sprint_range_end = 70
sprints_to_analyze = [f'Sprint {i}' for i in range(sprint_range_start, sprint_range_end + 1)]

def parse_azure_date(date_string):
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return None

def get_sprint_dates(iterations, sprint_name):
    for iteration in iterations:
        if iteration['name'] == sprint_name:
            return (
                datetime.strptime(iteration['attributes']['startDate'], '%Y-%m-%dT%H:%M:%SZ'),
                datetime.strptime(iteration['attributes']['finishDate'], '%Y-%m-%dT%H:%M:%SZ')
            )
    return None, None

def get_all_iterations():
    url = f'https://dev.azure.com/{organization}/{project}/{team}/_apis/work/teamsettings/iterations?api-version=6.0'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching iterations. Status code: {response.status_code}")
        print(response.text)
        return []
    return response.json()['value']

def get_work_item_history(work_item_id):
    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workItems/{work_item_id}/updates?api-version=6.0'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching work item history for ID {work_item_id}. Status code: {response.status_code}")
        return []
    return response.json()['value']

def check_previous_sprint_activity(work_item_id, current_sprint_path, iterations):
    history = get_work_item_history(work_item_id)
    if not history:
        return False
    
    # Get mapping of sprint names to paths
    sprint_paths = {iter['name']: iter.get('path', '') for iter in iterations}
    previous_sprint = f"Sprint {int(current_sprint.split()[1]) - 1}"
    previous_sprint_path = sprint_paths.get(previous_sprint, '')
    
    # Get in-progress states
    in_progress_states = ['In Development', 'In Progress', 'Ready for QA', 'QA', 'Code Review']
    
    for update in history:
        if 'fields' in update and 'System.State' in update['fields']:
            state_change = update['fields']['System.State']
            if 'newValue' in state_change and state_change['newValue'] in in_progress_states:
                # Check if this state change occurred during the previous sprint
                if 'fields' in update and 'System.IterationPath' in update['fields']:
                    iter_path = update['fields']['System.IterationPath']
                    if 'oldValue' in iter_path and iter_path['oldValue'] == previous_sprint_path:
                        return True
                    if 'newValue' in iter_path and iter_path['newValue'] == previous_sprint_path:
                        return True
                
                # If we don't have iteration path in this update, check the revision date
                revision_date = parse_azure_date(update.get('revisedDate'))
                if revision_date:
                    # Get previous sprint dates
                    prev_start, prev_end = get_sprint_dates(iterations, previous_sprint)
                    if prev_start and prev_end and prev_start <= revision_date <= prev_end:
                        return True
    
    return False

def get_sprint_data(sprint_name):
    sprint_data = {
        'user_stories_total': 0,
        'user_stories_completed': 0,
        'bugs_completed': 0,
        'points_committed': 0,
        'points_completed': 0,
        'initial_points_committed': 0,
        'carry_over_points': 0
    }

    iterations = get_all_iterations()
    if not iterations:
        return sprint_data

    iteration_path = next((iter.get('path', '') for iter in iterations if iter['name'] == sprint_name), None)
    if not iteration_path:
        return sprint_data

    sprint_start, sprint_end = get_sprint_dates(iterations, sprint_name)
    if not sprint_start or not sprint_end:
        return sprint_data
    sprint_end_eod = sprint_end.replace(hour=23, minute=59, second=59, microsecond=999999)

    query = {
        'query': f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], 
                   [Microsoft.VSTS.Scheduling.StoryPoints], [System.State], 
                   [System.CreatedDate], [System.ChangedDate]
            FROM workitems 
            WHERE [System.IterationPath] = '{iteration_path}'
        """
    }
    response = requests.post(f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0', 
                           headers=headers, json=query)
    if response.status_code != 200:
        return sprint_data

    work_items = response.json().get('workItems', [])
    if not work_items:
        return sprint_data

    work_item_ids = [str(item['id']) for item in work_items]
    batch_url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems?ids={",".join(work_item_ids)}&api-version=6.0'
    response = requests.get(batch_url, headers=headers)
    if response.status_code != 200:
        return sprint_data

    for item in response.json()['value']:
        item_id = item['id']
        fields = item['fields']
        item_type = fields['System.WorkItemType']
        state = fields['System.State']
        points = fields.get('Microsoft.VSTS.Scheduling.StoryPoints', 0) or 0
        title = fields.get('System.Title', 'No Title')
        
        created_date = parse_azure_date(fields.get('System.CreatedDate'))
        closed_date = parse_azure_date(fields.get('Microsoft.VSTS.Common.ClosedDate'))
        changed_date = parse_azure_date(fields.get('System.ChangedDate'))
        
        print(f"\nAnalyzing: {title}")
        print(f"State: {state}")
        print(f"Points: {points}")
        print(f"Created: {created_date}")
        print(f"Closed: {closed_date}")
        print(f"Changed: {changed_date}")
        print(f"Sprint window: {sprint_start} to {sprint_end_eod}")

        if item_type == 'User Story':
            sprint_data['user_stories_total'] += 1
            
            if created_date and created_date <= sprint_start:
                sprint_data['initial_points_committed'] += points
            sprint_data['points_committed'] += points
            
            # Check if this is a carry-over story from a previous sprint
            is_from_previous_sprint = check_previous_sprint_activity(item_id, iteration_path, iterations)
            is_not_done = state not in ['Closed', 'Done']
            
            if is_from_previous_sprint:
                print(f"🔄 Work on this story began in a previous sprint")
                sprint_data['carry_over_points'] += points
                print(f"🚧 Identified as carry-over story. Points: {points}")
            elif is_not_done and changed_date and sprint_start <= changed_date <= sprint_end_eod:
                sprint_data['carry_over_points'] += points
                print(f"🚧 Identified as carry-over story within current sprint. Points: {points}")
            
            if state in ['Closed', 'Done'] and closed_date and sprint_start <= closed_date <= sprint_end_eod:
                sprint_data['user_stories_completed'] += 1
                sprint_data['points_completed'] += points
                print(f"✅ Adding to completed stories. New total: {sprint_data['user_stories_completed']}")
            else:
                print("❌ Not counting this item because:")
                if state not in ['Closed', 'Done']:
                    print("  - Item is not Closed/Done")
                if not closed_date:
                    print("  - No closed date")
                if closed_date and (closed_date < sprint_start or closed_date > sprint_end_eod):
                    print("  - Closed date outside sprint window")
                
        elif item_type == 'Bug' and state in ['Closed', 'Done'] and closed_date and sprint_start <= closed_date <= sprint_end_eod:
            sprint_data['bugs_completed'] += 1

    return sprint_data

def create_output_folder():
    base_dir = 'sprint_reports'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    current_date = datetime.now().strftime('%Y%m%d')
    sprint_number = current_sprint.split()[-1]
    sprint_folder = f"{base_dir}/sprint{sprint_number}_{current_date}"
    if not os.path.exists(sprint_folder):
        os.makedirs(sprint_folder)
    
    return sprint_folder

def create_velocity_graph(all_sprint_data, output_folder):
    plt.figure(figsize=(8, 6))
    last_three = list(all_sprint_data.items())[-3:]
    
    stories = [d['user_stories_completed'] for _, d in last_three]
    adjusted_points = [d['points_completed'] for _, d in last_three]
    
    x = np.arange(2)
    width = 0.5
    
    plt.bar(x[0], np.mean(stories), width, color='#4A90E2', label='User Story')
    plt.bar(x[1], np.mean(adjusted_points), width, color='#F5A623', label='Story Point')
    
    plt.title('3 Sprint Rolling Avg User Story &\nStory Point Velocity', pad=20)
    plt.xticks([])
    
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    for i, v in enumerate([np.mean(stories), np.mean(adjusted_points)]):
        plt.text(i, float(v), f'{int(v)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/velocity_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_bugs_graph(all_sprint_data, output_folder):
    plt.figure(figsize=(10, 6))
    last_five = list(all_sprint_data.items())[-5:]
    
    sprints = [s.split()[-1] for s, _ in last_five]
    bugs = [d['bugs_completed'] for _, d in last_five]
    
    bars = plt.bar(sprints, bugs, color='#4A90E2', width=0.6)
    
    title = f'Bugs Done\nSprints {sprint_range_start} - {sprint_range_end}'
    plt.title(title, pad=20)
    plt.xlabel('')
    plt.ylabel('')
    
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., float(height),
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/bugs_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_commitment_graph(all_sprint_data, output_folder):
    plt.figure(figsize=(12, 6))
    sprints = [s.split()[-1] for s in all_sprint_data.keys()]
    
    user_stories = [d['user_stories_completed'] for d in all_sprint_data.values()]
    bugs = [d['bugs_completed'] for d in all_sprint_data.values()]
    points_committed = [d['initial_points_committed'] - d['carry_over_points'] for d in all_sprint_data.values()]
    points_completed = [d['points_completed'] for d in all_sprint_data.values()]
    
    x = np.arange(len(sprints))
    width = 0.2
    
    plt.bar(x - width*1.5, user_stories, width, color='#F5A623', label='User Stories Done')
    plt.bar(x - width/2, bugs, width, color='#4A90E2', label='Bugs Done')
    plt.bar(x + width/2, points_committed, width, color='#7ED321', label='Points Committed')
    plt.bar(x + width*1.5, points_completed, width, color='#9B51E0', label='Points Completed')
    
    plt.title('Sprint Commitment vs. Actuals Summary\n5 Sprint, 10 Week Trend', pad=20)
    plt.xlabel('')
    plt.ylabel('')
    
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.xticks(x, sprints)
    
    for i in range(len(sprints)):
        metrics = [user_stories[i], bugs[i], points_committed[i], points_completed[i]]
        positions = [i - width*1.5, i - width/2, i + width/2, i + width*1.5]
        
        for value, position in zip(metrics, positions):
            plt.text(position, float(value), str(int(value)),
                    ha='center', va='bottom')
    
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.subplots_adjust(right=0.85)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/commitment_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_sprint_stats_graph(sprint_data, output_folder):
    plt.figure(figsize=(8, 6))
    plt.clf()
    
    adjusted_points_committed = sprint_data['points_committed'] - sprint_data['carry_over_points']
    points_completion_pct = round((sprint_data['points_completed'] / adjusted_points_committed) * 100) if adjusted_points_committed > 0 else 0
    
    sprint_number = current_sprint.split()[-1]
    
    text_elements = [
        (f'Sprint {sprint_number} Stats', 'black', 20, 0.95),
        (f'Total User Stories Committed: {sprint_data["user_stories_total"]}', '#FF8C00', 14, 0.90),
        (f'Total Done: {sprint_data["user_stories_completed"]}', '#0078D7', 14, 0.85),
        (f'Total Story Points Committed: {adjusted_points_committed}', '#FF8C00', 14, 0.80),
        (f'Total Done: {sprint_data["points_completed"]}', '#0078D7', 14, 0.75),
        (f'Completion: {points_completion_pct}%', 'black', 16, 0.70)
    ]
    
    fig = plt.figure(figsize=(8, 6))
    fig.patch.set_facecolor('white')
    
    ax = plt.gca()
    ax.set_facecolor('white')
    
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    for text, color, size, y_pos in text_elements:
        plt.text(0.5, float(y_pos), text,
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                color=color,
                fontsize=size,
                fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/sprint_stats.png', 
                dpi=300, 
                bbox_inches='tight',
                facecolor='white')
    plt.close()

def create_rolling_average_graph(all_sprint_data, output_folder):
    plt.figure(figsize=(15, 8))
    last_five = list(all_sprint_data.items())[-5:]
    
    sprints = [s.split()[-1] for s, _ in last_five]
    points = [d['points_completed'] for _, d in last_five]
    stories = [d['user_stories_completed'] for _, d in last_five]
    
    avg_points = np.mean(points)
    avg_stories = np.mean(stories)
    
    width = 0.35
    x = np.arange(len(sprints))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[1, 2])
    
    ax1.bar([0], [avg_points], width, color='#F5A623', label='Avg Points')
    ax1.bar([1], [avg_stories], width, color='#4A90E2', label='Avg Stories')
    
    for i, v in enumerate([avg_points, avg_stories]):
        ax1.text(i, float(v), f'{int(v)}', ha='center', va='bottom')
    
    ax1.set_title('5 Sprint Rolling Average', pad=20)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['Points', 'Stories'])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    ax2.bar(x - width/2, points, width, color='#F5A623', label='Points')
    ax2.bar(x + width/2, stories, width, color='#4A90E2', label='Stories')
    
    for i in range(len(sprints)):
        ax2.text(i - width/2, float(points[i]), str(int(points[i])), ha='center', va='bottom')
        ax2.text(i + width/2, float(stories[i]), str(int(stories[i])), ha='center', va='bottom')
    
    ax2.set_title('Individual Sprint Performance', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(sprints)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/rolling_average_graph.png', dpi=300, bbox_inches='tight')
    plt.close()


def main():
    output_folder = create_output_folder()
    
    all_sprint_data = {}
    for sprint in sprints_to_analyze:
        all_sprint_data[sprint] = get_sprint_data(sprint)
    
    report_path = f'{output_folder}/sprintReport.txt'
    with open(report_path, 'w') as f:
        f.write("Sprint Analysis Report\n")
        f.write("====================\n\n")
        
    create_velocity_graph(all_sprint_data, output_folder)
    create_bugs_graph(all_sprint_data, output_folder)
    create_commitment_graph(all_sprint_data, output_folder)
    create_rolling_average_graph(all_sprint_data, output_folder)
    
    current_sprint_data = all_sprint_data[current_sprint]
    create_sprint_stats_graph(current_sprint_data, output_folder)
    
    print(f"\nAnalysis complete. Results written to: {output_folder}")
    print(f"- {output_folder}/sprintReport.txt")
    print(f"- {output_folder}/velocity_graph.png")
    print(f"- {output_folder}/bugs_graph.png")
    print(f"- {output_folder}/commitment_graph.png")
    print(f"- {output_folder}/sprint_stats.png")
    print(f"- {output_folder}/rolling_average_graph.png")

if __name__ == "__main__":
    main()
