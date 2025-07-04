import requests
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import json

organization: str = 'Legislative'
project: str = 'LegBone'
team: str = 'LegBone Team'
token: str = os.getenv('AZURE_TOKEN')
encoded_token: str = base64.b64encode(f':{token}'.encode()).decode()
headers: dict = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_token}'
}

current_sprint: str = 'Sprint 77'
sprint_range_start: int = 72
sprint_range_end: int = 78
sprints_to_analyze: list[str] = [f'Sprint {i}' for i in range(sprint_range_start, sprint_range_end)]
carryover_data_file: str = 'sprint_carryover_data.json'
override_data_file: str = 'sprint_override_data.json'

def parse_azure_date(date_string: str) -> datetime:
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return None

def get_sprint_dates(iterations: list, sprint_name: str) -> tuple:
    for iteration in iterations:
        if iteration['name'] == sprint_name:
            return (
                datetime.strptime(iteration['attributes']['startDate'], '%Y-%m-%dT%H:%M:%SZ'),
                datetime.strptime(iteration['attributes']['finishDate'], '%Y-%m-%dT%H:%M:%SZ')
            )
    return None, None

def get_sprint_data(sprint_name: str, override_data: dict) -> dict:
    sprint_data: dict = {
        'user_stories_total': 0,
        'user_stories_completed': 0,
        'bugs_completed': 0,
        'points_committed': 0,
        'points_completed': 0,
        'initial_points_committed': 0
    }

    url: str = f'https://dev.azure.com/{organization}/{project}/{team}/_apis/work/teamsettings/iterations?api-version=6.0'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching sprint data for {sprint_name}. Status code: {response.status_code}")
        print(response.text)
        return sprint_data

    iterations: list = response.json()['value']
    iteration_path: str = next((iter.get('path', '') for iter in iterations if iter['name'] == sprint_name), None)
    if not iteration_path:
        return sprint_data

    sprint_start, sprint_end = get_sprint_dates(iterations, sprint_name)
    if not sprint_start or not sprint_end:
        return sprint_data
    sprint_end_eod: datetime = sprint_end.replace(hour=23, minute=59, second=59, microsecond=999999)

    query: dict = {
        'query': f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], 
                   [Microsoft.VSTS.Scheduling.StoryPoints], [System.State]
            FROM workitems 
            WHERE [System.IterationPath] = '{iteration_path}'
        """
    }
    response = requests.post(f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0', 
                           headers=headers, json=query)
    if response.status_code != 200:
        return sprint_data

    work_items: list = response.json().get('workItems', [])
    if not work_items:
        return sprint_data

    work_item_ids: list[str] = [str(item['id']) for item in work_items]
    batch_url: str = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems?ids={",".join(work_item_ids)}&api-version=6.0'
    response = requests.get(batch_url, headers=headers)
    if response.status_code != 200:
        return sprint_data

    for item in response.json()['value']:
        fields: dict = item['fields']
        item_type: str = fields['System.WorkItemType']
        state: str = fields['System.State']
        points: int = fields.get('Microsoft.VSTS.Scheduling.StoryPoints', 0) or 0
        title: str = fields.get('System.Title', 'No Title')
        
        created_date: datetime = parse_azure_date(fields.get('System.CreatedDate'))
        closed_date: datetime = parse_azure_date(fields.get('Microsoft.VSTS.Common.ClosedDate'))
        
        print(f"\nAnalyzing: {title}")
        print(f"State: {state}")
        print(f"Points: {points}")
        print(f"Created: {created_date}")
        print(f"Closed: {closed_date}")
        print(f"Sprint window: {sprint_start} to {sprint_end_eod}")

        if state == 'Removed':
            print(f"❌ Skipping item with state 'Removed': {title}")
            continue

        if item_type == 'User Story':
            sprint_data['user_stories_total'] += 1
            
            if created_date and created_date <= sprint_start:
                sprint_data['initial_points_committed'] += points
            sprint_data['points_committed'] += points
            
            if state == 'Closed' and closed_date and sprint_start <= closed_date <= sprint_end_eod:
                sprint_data['user_stories_completed'] += 1
                sprint_data['points_completed'] += points
                print(f"✅ Adding to completed stories. New total: {sprint_data['user_stories_completed']}")
            else:
                print("❌ Not counting this item because:")
                if state != 'Closed':
                    print("  - Item is not Closed")
                if not closed_date:
                    print("  - No closed date")
                if closed_date and (closed_date < sprint_start or closed_date > sprint_end_eod):
                    print("  - Closed date outside sprint window")
                
        elif item_type == 'Bug' and state == 'Closed' and closed_date and sprint_start <= closed_date <= sprint_end_eod:
            sprint_data['bugs_completed'] += 1

    override_sprint_data: dict = override_data.get(sprint_name, {})
    if 'stories_committed' in override_sprint_data:
        print(f"🔄 Overriding stories committed for {sprint_name}: {sprint_data['user_stories_total']} -> {override_sprint_data['stories_committed']}")
        sprint_data['user_stories_total'] = override_sprint_data['stories_committed']
    
    if 'points_committed' in override_sprint_data:
        print(f"🔄 Overriding points committed for {sprint_name}: {sprint_data['points_committed']} -> {override_sprint_data['points_committed']}")
        sprint_data['points_committed'] = override_sprint_data['points_committed']

    return sprint_data

def load_carryover_data() -> dict:
    if os.path.exists(carryover_data_file):
        with open(carryover_data_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_carryover_data(carryover_data: dict) -> None:
    with open(carryover_data_file, 'w') as f:
        json.dump(carryover_data, f, indent=2)

def load_override_data() -> dict:
    if os.path.exists(override_data_file):
        with open(override_data_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_override_data(override_data: dict) -> None:
    with open(override_data_file, 'w') as f:
        json.dump(override_data, f, indent=2)

def create_output_folder() -> str:
    base_dir: str = 'sprint_reports'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    current_date: str = datetime.now().strftime('%Y%m%d')
    sprint_number: str = current_sprint.split()[-1]
    sprint_folder: str = f"{base_dir}/sprint{sprint_number}_{current_date}"
    if not os.path.exists(sprint_folder):
        os.makedirs(sprint_folder)
    
    return sprint_folder

def create_velocity_graph(all_sprint_data: dict, output_folder: str, carryover_data: dict) -> None:
    plt.figure(figsize=(8, 6))
    last_three: list = list(all_sprint_data.items())[-3:]
    
    stories: list[int] = [d['user_stories_completed'] for s, d in last_three]
    points: list[int] = [d['points_completed'] for s, d in last_three]
    
    x: np.ndarray = np.arange(2)
    width: float = 0.5
    
    plt.bar(x[0], np.mean(stories), width, color='#4A90E2', label='User Story')
    plt.bar(x[1], np.mean(points), width, color='#F5A623', label='Story Point')
    
    plt.title('3 Sprint Rolling Avg User Story &\nStory Point Velocity', pad=20)
    plt.xticks([])
    
    for i, v in enumerate([np.mean(stories), np.mean(points)]):
        plt.text(i, v, f'{int(v)}', ha='center', va='bottom')
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/velocity_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_bugs_graph(all_sprint_data: dict, output_folder: str) -> None:
    plt.figure(figsize=(10, 6))
    last_five: list = list(all_sprint_data.items())[-5:]
    
    sprints: list[str] = [s.split()[-1] for s, _ in last_five]
    bugs: list[int] = [d['bugs_completed'] for _, d in last_five]
    
    bars = plt.bar(sprints, bugs, color='#4A90E2', width=0.6)
    
    title: str = f'Bugs Done\nSprints {sprint_range_start} - {sprint_range_end - 1}'
    plt.title(title, pad=20)
    plt.xlabel('')
    plt.ylabel('')
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    for bar in bars:
        height: float = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/bugs_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_commitment_graph(all_sprint_data: dict, output_folder: str, carryover_data: dict, override_data: dict) -> None:
    plt.figure(figsize=(12, 6))
    sprints: list[str] = [s.split()[-1] for s in all_sprint_data.keys()]
    
    user_stories_committed: list[int] = []
    user_stories_completed: list[int] = []
    points_committed: list[float] = []
    points_completed: list[int] = []
    bugs: list[int] = []
    
    for sprint_name, d in all_sprint_data.items():
        co_tickets: int = carryover_data.get(sprint_name, {}).get('tickets', 0)
        co_points: int = carryover_data.get(sprint_name, {}).get('points', 0)
        
        override_sprint_data: dict = override_data.get(sprint_name, {})
        
        if 'stories_committed' in override_sprint_data:
            user_stories_committed.append(override_sprint_data['stories_committed'])
        else:
            user_stories_committed.append(d['user_stories_total'] + co_tickets)
        
        user_stories_completed.append(d['user_stories_completed'])
        
        if 'points_committed' in override_sprint_data:
            points_committed.append(override_sprint_data['points_committed'])
        else:
            points_committed.append(d['points_committed'] + co_points)
        
        points_completed.append(d['points_completed'])
        bugs.append(d['bugs_completed'])
    
    x: np.ndarray = np.arange(len(sprints))
    width: float = 0.2
    
    plt.bar(x - width*1.5, user_stories_completed, width, color='#F5A623', label='User Stories Done')
    plt.bar(x - width/2, bugs, width, color='#4A90E2', label='Bugs Done')
    plt.bar(x + width/2, points_committed, width, color='#7ED321', label='Points Committed')
    plt.bar(x + width*1.5, points_completed, width, color='#9B51E0', label='Points Completed')
    
    plt.title('Sprint Commitment vs. Actuals Summary\n5 Sprint, 10 Week Trend', pad=20)
    plt.xlabel('')
    plt.ylabel('')
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.xticks(x, sprints)
    
    for i in range(len(sprints)):
        metrics: list[int] = [user_stories_completed[i], bugs[i], points_committed[i], points_completed[i]]
        positions: list[float] = [i - width*1.5, i - width/2, i + width/2, i + width*1.5]
        
        for value, position in zip(metrics, positions):
            plt.text(position, value, str(int(value)),
                    ha='center', va='bottom')
    
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.subplots_adjust(right=0.85)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/commitment_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_sprint_stats_graph(sprint_data: dict, output_folder: str, carryover_data: dict, override_data: dict) -> None:
    sprint_name: str = current_sprint
    co_tickets: int = carryover_data.get(sprint_name, {}).get('tickets', 0)
    co_points: int = carryover_data.get(sprint_name, {}).get('points', 0)
    
    plt.figure(figsize=(8, 6))
    plt.clf()
    
    points_completed: int = sprint_data['points_completed']
    stories_completed: int = sprint_data['user_stories_completed']
    
    override_sprint_data: dict = override_data.get(sprint_name, {})
    
    if 'stories_committed' in override_sprint_data:
        stories_committed: int = override_sprint_data['stories_committed']
    else:
        stories_committed: int = sprint_data['user_stories_total'] + co_tickets
    
    if 'points_committed' in override_sprint_data:
        points_committed: float = override_sprint_data['points_committed']
    else:
        points_committed: float = sprint_data['points_committed'] + co_points
    
    points_completion_pct: int = round((points_completed / points_committed) * 100) if points_committed > 0 else 0
    
    sprint_number: str = current_sprint.split()[-1]
    
    text_elements: list[tuple] = [
        (f'Sprint {sprint_number} Stats', 'black', 20, 0.95),
        (f'Total User Stories Committed: {stories_committed}', '#FF8C00', 14, 0.90),
        (f'Total Done: {stories_completed}', '#0078D7', 14, 0.85),
        (f'Total Story Points Committed: {points_committed}', '#FF8C00', 14, 0.80),
        (f'Total Done: {points_completed}', '#0078D7', 14, 0.75),
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
        plt.text(0.5, y_pos, text,
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

def create_rolling_average_graph(all_sprint_data: dict, output_folder: str, carryover_data: dict) -> None:
    plt.figure(figsize=(15, 8))
    last_five: list = list(all_sprint_data.items())[-5:]
    
    sprints: list[str] = [s.split()[-1] for s, _ in last_five]
    points: list[int] = [d['points_completed'] for s, d in last_five]
    stories: list[int] = [d['user_stories_completed'] for s, d in last_five]
    
    avg_points: float = np.mean(points)
    avg_stories: float = np.mean(stories)
    
    width: float = 0.35
    x: np.ndarray = np.arange(len(sprints))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[1, 2])
    
    ax1.bar([0], [avg_points], width, color='#F5A623', label='Avg Points')
    ax1.bar([1], [avg_stories], width, color='#4A90E2', label='Avg Stories')
    
    for i, v in enumerate([avg_points, avg_stories]):
        ax1.text(i, v, f'{int(v)}', ha='center', va='bottom')
    
    ax1.set_title('5 Sprint Rolling Average', pad=20)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['Points', 'Stories'])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    ax2.bar(x - width/2, points, width, color='#F5A623', label='Points')
    ax2.bar(x + width/2, stories, width, color='#4A90E2', label='Stories')
    
    for i in range(len(sprints)):
        ax2.text(i - width/2, points[i], str(int(points[i])), ha='center', va='bottom')
        ax2.text(i + width/2, stories[i], str(int(stories[i])), ha='center', va='bottom')
    
    ax2.set_title('Individual Sprint Performance', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(sprints)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_folder}/rolling_average_graph.png', dpi=300, bbox_inches='tight')
    plt.close()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Generate sprint analysis reports with carry-over and override adjustments')
    parser.add_argument('--cotickets', type=int, default=0, help='Number of tickets carried over')
    parser.add_argument('--copoints', type=int, default=0, help='Number of points carried over')
    parser.add_argument('--stories-committed', type=int, help='Override stories committed for current sprint')
    parser.add_argument('--points-committed', type=float, help='Override points committed for current sprint')
    parser.add_argument('--sprint', type=str, help=f'Sprint to apply overrides to (default: {current_sprint})', default=current_sprint)
    args = parser.parse_args()
    
    carry_over_tickets: int = args.cotickets
    carry_over_points: int = args.copoints
    override_stories_committed: int = args.stories_committed
    override_points_committed: float = args.points_committed
    target_sprint: str = args.sprint
    
    print(f"Target sprint: {target_sprint}")
    print(f"Carry-over tickets: {carry_over_tickets}")
    print(f"Carry-over points: {carry_over_points}")
    if override_stories_committed is not None:
        print(f"Override stories committed: {override_stories_committed}")
    if override_points_committed is not None:
        print(f"Override points committed: {override_points_committed}")
    
    carryover_data: dict = load_carryover_data()
    override_data: dict = load_override_data()
    
    if carry_over_tickets > 0 or carry_over_points > 0:
        if target_sprint not in carryover_data:
            carryover_data[target_sprint] = {}
        carryover_data[target_sprint]['tickets'] = carry_over_tickets
        carryover_data[target_sprint]['points'] = carry_over_points
        save_carryover_data(carryover_data)
        print(f"Saved carry-over data for {target_sprint} to {carryover_data_file}")
    
    if override_stories_committed is not None or override_points_committed is not None:
        if target_sprint not in override_data:
            override_data[target_sprint] = {}
        if override_stories_committed is not None:
            override_data[target_sprint]['stories_committed'] = override_stories_committed
        if override_points_committed is not None:
            override_data[target_sprint]['points_committed'] = override_points_committed
        save_override_data(override_data)
        print(f"Saved override data for {target_sprint} to {override_data_file}")
    
    output_folder: str = create_output_folder()
    
    all_sprint_data: dict = {}
    for sprint in sprints_to_analyze:
        all_sprint_data[sprint] = get_sprint_data(sprint, override_data)
    
    report_path: str = f'{output_folder}/sprintReport.txt'
    with open(report_path, 'w') as f:
        f.write("Sprint Analysis Report\n")
        f.write("====================\n\n")
        
        for sprint_name, sprint_data in all_sprint_data.items():
            co_tickets: int = carryover_data.get(sprint_name, {}).get('tickets', 0)
            co_points: int = carryover_data.get(sprint_name, {}).get('points', 0)
            
            override_sprint_data: dict = override_data.get(sprint_name, {})
            
            if 'stories_committed' in override_sprint_data:
                adjusted_stories_committed: int = override_sprint_data['stories_committed']
            else:
                adjusted_stories_committed: int = sprint_data['user_stories_total'] + co_tickets
            
            if 'points_committed' in override_sprint_data:
                adjusted_points_committed: float = override_sprint_data['points_committed']
            else:
                adjusted_points_committed: float = sprint_data['points_committed'] + co_points
            
            f.write(f"{sprint_name}:\n")
            if co_tickets > 0 or co_points > 0:
                f.write(f"  Carry-over tickets: {co_tickets}\n")
                f.write(f"  Carry-over points: {co_points}\n")
            
            override_sprint_data: dict = override_data.get(sprint_name, {})
            if 'stories_committed' in override_sprint_data or 'points_committed' in override_sprint_data:
                f.write(f"  ** OVERRIDES APPLIED **\n")
                if 'stories_committed' in override_sprint_data:
                    f.write(f"  Final Stories Committed: {override_sprint_data['stories_committed']}\n")
                if 'points_committed' in override_sprint_data:
                    f.write(f"  Final Points Committed: {override_sprint_data['points_committed']}\n")
            
            f.write(f"  Azure Stories Committed: {sprint_data['user_stories_total']}\n")
            f.write(f"  Final Stories Committed (with adjustments): {adjusted_stories_committed}\n")
            f.write(f"  Stories Completed: {sprint_data['user_stories_completed']}\n")
            f.write(f"  Azure Points Committed: {sprint_data['points_committed']}\n")
            f.write(f"  Final Points Committed (with adjustments): {adjusted_points_committed}\n")
            f.write(f"  Points Completed: {sprint_data['points_completed']}\n\n")
        
    create_velocity_graph(all_sprint_data, output_folder, carryover_data)
    create_bugs_graph(all_sprint_data, output_folder)
    create_commitment_graph(all_sprint_data, output_folder, carryover_data, override_data)
    create_rolling_average_graph(all_sprint_data, output_folder, carryover_data)
    
    current_sprint_data: dict = all_sprint_data[current_sprint]
    create_sprint_stats_graph(current_sprint_data, output_folder, carryover_data, override_data)
    
    print(f"\nAnalysis complete. Results written to: {output_folder}")
    print(f"- {output_folder}/sprintReport.txt")
    print(f"- {output_folder}/velocity_graph.png")
    print(f"- {output_folder}/bugs_graph.png")
    print(f"- {output_folder}/commitment_graph.png")
    print(f"- {output_folder}/sprint_stats.png")
    print(f"- {output_folder}/rolling_average_graph.png")

if __name__ == "__main__":
    main()
