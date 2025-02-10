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

current_sprint = 'Sprint 68'
sprints_to_analyze = [f'Sprint {i}' for i in range(64, 69)]

def parse_azure_date(date_string):
    if not date_string:
        return None
    try:
        # Try parsing with microseconds
        return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            # Try parsing without microseconds
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            print(f"Could not parse date: {date_string}")
            return None

def get_sprint_dates(iterations, sprint_name):
    for iteration in iterations:
        if iteration['name'] == sprint_name:
            return (
                datetime.strptime(iteration['attributes']['startDate'], '%Y-%m-%dT%H:%M:%SZ'),
                datetime.strptime(iteration['attributes']['finishDate'], '%Y-%m-%dT%H:%M:%SZ')
            )
    return None, None

def get_sprint_data(sprint_name):
    print(f"\nProcessing {sprint_name}...")
    sprint_data = {
        'user_stories_completed': 0,
        'bugs_completed': 0,
        'points_committed': 0,
        'points_completed': 0,
        'initial_points_committed': 0  # Points committed at sprint start
    }

    url = f'https://dev.azure.com/{organization}/{project}/{team}/_apis/work/teamsettings/iterations?api-version=6.0'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to get iterations: {response.status_code}")
        return sprint_data

    iterations = response.json()['value']
    iteration_path = None
    
    for iteration in iterations:
        if iteration['name'] == sprint_name:
            iteration_path = iteration.get('path', '')
            break
    
    if not iteration_path:
        print(f"Sprint {sprint_name} not found")
        return sprint_data

    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0'
    query = {
        'query': f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], 
                   [Microsoft.VSTS.Scheduling.StoryPoints], [System.State]
            FROM workitems 
            WHERE [System.IterationPath] = '{iteration_path}'
        """
    }
    
    response = requests.post(url, headers=headers, json=query)
    print('from workitems', response)
    
    if response.status_code != 200:
        print(f"WIQL query failed: {response.status_code}")
        return sprint_data

    work_items = response.json().get('workItems', [])
    if not work_items:
        print("No work items found")
        return sprint_data

    work_item_ids = [str(item['id']) for item in work_items]
    batch_url = f'''https://dev.azure.com/{organization}\
/{project}/_apis/wit/workitems?\
ids={",".join(work_item_ids)}&api-version=6.0'''
    print('batch_url', batch_url)
    response = requests.get(batch_url, headers=headers)
    print('from batch_url', response)
    
    if response.status_code != 200:
        print(f"Failed to get work item details: {response.status_code}")
        return sprint_data

    # Get sprint start/end dates
    # Check creation and closed dates
    created_date = parse_azure_date(item['fields']['System.CreatedDate'])
    closed_date = parse_azure_date(item['fields'].get('Microsoft.VSTS.Common.ClosedDate'))

    if not created_date:
        print(f"Warning: Could not parse creation date for item {item['id']}")
        continue
    if not sprint_start or not sprint_end:
        print(f"Could not determine sprint dates for {sprint_name}")
        return sprint_data
    
    print(f"Sprint dates: {sprint_start} to {sprint_end}")

    for item in response.json()['value']:
        item_type = item['fields']['System.WorkItemType']
        print('item_type', item_type)
        state = item['fields']['System.State']
        print('state', state)
        points = item['fields'].get('Microsoft.VSTS.Scheduling.StoryPoints', 0) or 0
        print('points', points)
        
        # Check creation and closed dates
        created_date = datetime.strptime(item['fields']['System.CreatedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        closed_date_str = item['fields'].get('Microsoft.VSTS.Common.ClosedDate')
        closed_date = datetime.strptime(closed_date_str, '%Y-%m-%dT%H:%M:%S.%fZ') if closed_date_str else None
        
        if item_type == 'User Story':
            # Track initial commitment (items that existed at sprint start)
            if created_date <= sprint_start:
                sprint_data['initial_points_committed'] += points
                print(f"Initial commitment: {points} points for story created on {created_date}")
            
            # Track current commitment
            sprint_data['points_committed'] += points
            
            # Track completed items
            if state == 'Closed' and closed_date and sprint_start <= closed_date <= sprint_end:
                sprint_data['user_stories_completed'] += 1
                sprint_data['points_completed'] += points
                print(f"Completed in sprint: {points} points, closed on {closed_date}")
                
        elif item_type == 'Bug' and state == 'Closed' and closed_date and sprint_start <= closed_date <= sprint_end:
            sprint_data['bugs_completed'] += 1

    print(f"Sprint {sprint_name} processed:")
    print(f"User Stories Done: {sprint_data['user_stories_completed']}")
    print(f"Bugs Done: {sprint_data['bugs_completed']}")
    print(f"Points Committed: {sprint_data['points_committed']}")
    print(f"Points Completed: {sprint_data['points_completed']}")
    
    return sprint_data

def create_velocity_graph(all_sprint_data):
    plt.figure(figsize=(10, 6))
    last_three = list(all_sprint_data.items())[-3:]
    
    stories = [d['user_stories_completed'] for _, d in last_three]
    points = [d['points_completed'] for _, d in last_three]
    
    x = np.arange(2)
    width = 0.35
    
    plt.bar(x[0], np.mean(stories), width, color='#4287f5', label='Avg User Stories')
    plt.bar(x[1], np.mean(points), width, color='#f5a142', label='Avg Story Points')
    
    plt.title('3 Sprint Rolling Avg User Story & Story Point Velocity')
    plt.xticks(x, ['User Stories', 'Story Points'])
    plt.ylabel('Average')
    plt.legend()
    plt.tight_layout()
    plt.savefig('velocity_graph.png')
    plt.close()

def create_bugs_graph(all_sprint_data):
    plt.figure(figsize=(10, 6))
    last_five = list(all_sprint_data.items())[-5:]
    
    sprints = [s.split()[-1] for s, _ in last_five]
    bugs = [d['bugs_completed'] for _, d in last_five]
    
    plt.bar(sprints, bugs, color='#4287f5')
    plt.title('Bugs Done - Last 5 Sprints')
    plt.xlabel('Sprint')
    plt.ylabel('Bugs Completed')
    plt.tight_layout()
    plt.savefig('bugs_graph.png')
    plt.close()

def create_commitment_graph(all_sprint_data):
    plt.figure(figsize=(12, 6))
    sprints = [s.split()[-1] for s in all_sprint_data.keys()]
    
    user_stories = [d['user_stories_completed'] for d in all_sprint_data.values()]
    bugs = [d['bugs_completed'] for d in all_sprint_data.values()]
    points_committed = [d['initial_points_committed'] for d in all_sprint_data.values()]  # Use initial commitment
    points_completed = [d['points_completed'] for d in all_sprint_data.values()]
    
    x = np.arange(len(sprints))
    width = 0.2
    
    plt.bar(x - width*1.5, user_stories, width, color='#f7dc6f', label='User Stories Done')
    plt.bar(x - width/2, bugs, width, color='#85c1e9', label='Bugs Done')
    plt.bar(x + width/2, points_committed, width, color='#82e0aa', label='Points Committed')
    plt.bar(x + width*1.5, points_completed, width, color='#3498db', label='Points Completed')
    
    plt.title('Sprint Commitment vs. Actuals Summary')
    plt.xlabel('Sprint')
    plt.ylabel('Count')
    plt.xticks(x, sprints)
    plt.legend()
    plt.tight_layout()
    plt.savefig('commitment_graph.png')
    plt.close()

all_sprint_data = {}
for sprint in sprints_to_analyze:
    all_sprint_data[sprint] = get_sprint_data(sprint)

with open('sprintReport.txt', 'w') as f:
    f.write("Sprint Analysis Report\n")
    f.write("====================\n\n")
    
    f.write("Rolling Average (Last 3 Sprints):\n")
    last_three = list(all_sprint_data.items())[-3:]
    avg_stories = sum(d['user_stories_completed'] for _, d in last_three) / 3
    avg_points = sum(d['points_completed'] for _, d in last_three) / 3
    f.write(f"Average User Stories: {avg_stories:.1f}\n")
    f.write(f"Average Story Points: {avg_points:.1f}\n\n")
    
    f.write("Bugs Done (Last 5 Sprints):\n")
    for sprint, data in list(all_sprint_data.items())[-5:]:
        f.write(f"{sprint}: {data['bugs_completed']}\n")
    f.write("\n")
    
    f.write("Sprint Metrics:\n")
    for sprint, data in all_sprint_data.items():
        f.write(f"\n{sprint}:\n")
        f.write(f"User Stories Completed: {data['user_stories_completed']}\n")
        f.write(f"Bugs Done: {data['bugs_completed']}\n")
        f.write(f"Points Committed: {data['points_committed']}\n")
        f.write(f"Points Completed: {data['points_completed']}\n")

print("\nGenerating graphs...")
create_velocity_graph(all_sprint_data)
create_bugs_graph(all_sprint_data)
create_commitment_graph(all_sprint_data)

print("\nAnalysis complete. Results written to:")
print("- sprintReport.txt")
print("- velocity_graph.png")
print("- bugs_graph.png")
print("- commitment_graph.png")
