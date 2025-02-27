import requests
import base64
from datetime import datetime
import os
import json

# Configuration
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
next_sprint = 'Sprint 71'

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

def get_sprint_iterations_data():
    """Get all iteration data for the project"""
    url = f'https://dev.azure.com/{organization}/{project}/{team}/_apis/work/teamsettings/iterations?api-version=6.0'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching iterations. Status code: {response.status_code}")
        print(response.text)
        return []
        
    return response.json()['value']

def get_sprint_dates(iterations, sprint_name):
    for iteration in iterations:
        if iteration['name'] == sprint_name:
            return (
                parse_azure_date(iteration['attributes']['startDate']),
                parse_azure_date(iteration['attributes']['finishDate'])
            )
    return None, None

def get_work_items_by_iteration_path(iteration_path):
    """Get all work items for a specific iteration path"""
    query = {
        'query': f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType], 
                   [Microsoft.VSTS.Scheduling.StoryPoints], [System.State],
                   [System.IterationPath], [System.CreatedDate], [System.ChangedDate]
            FROM workitems 
            WHERE [System.IterationPath] = '{iteration_path}'
        """
    }
    
    response = requests.post(f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0', 
                           headers=headers, json=query)
    if response.status_code != 200:
        print(f"Error querying work items. Status code: {response.status_code}")
        print(response.text)
        return []

    work_items = response.json().get('workItems', [])
    if not work_items:
        return []
        
    work_item_ids = [str(item['id']) for item in work_items]
    batch_url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems?ids={",".join(work_item_ids)}&api-version=6.0'
    response = requests.get(batch_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching work items. Status code: {response.status_code}")
        print(response.text)
        return []
        
    return response.json()['value']

def get_work_item_history(work_item_id):
    """Get the history of a work item to track iteration changes"""
    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{work_item_id}/updates?api-version=6.0'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching work item history. Status code: {response.status_code}")
        print(response.text)
        return []
        
    return response.json()['value']

def debug_carryover_stories(current_sprint_items, next_sprint_items, iterations):
    """Debug version of find_carryover_stories with detailed logging"""
    # Get iteration paths and dates
    current_iteration_path = None
    next_iteration_path = None
    current_sprint_start = None
    current_sprint_end = None
    
    for iteration in iterations:
        if iteration['name'] == current_sprint:
            current_iteration_path = iteration.get('path', '')
            if 'attributes' in iteration:
                current_sprint_start = parse_azure_date(iteration['attributes'].get('startDate'))
                current_sprint_end = parse_azure_date(iteration['attributes'].get('finishDate'))
        elif iteration['name'] == next_sprint:
            next_iteration_path = iteration.get('path', '')
    
    print(f"Current Sprint Path: {current_iteration_path}")
    print(f"Next Sprint Path: {next_iteration_path}")
    print(f"Current Sprint Start: {current_sprint_start}")
    print(f"Current Sprint End: {current_sprint_end}")
    
    if not current_iteration_path or not next_iteration_path:
        print("Error: Could not find iteration paths")
        return []
    
    # Create lookup dictionaries for more efficient access
    next_sprint_items_dict = {item['id']: item for item in next_sprint_items}
    
    # Create sets for analysis
    next_sprint_ids = set(next_sprint_items_dict.keys())
    current_sprint_ids = {item['id'] for item in current_sprint_items}
    
    # Items that appear in both sprints
    common_items = current_sprint_ids.intersection(next_sprint_ids)
    print(f"\nItems appearing in both sprints: {len(common_items)}")
    for item_id in common_items:
        for item in current_sprint_items:
            if item['id'] == item_id:
                print(f"  - {item['fields'].get('System.Title', 'No Title')} (ID: {item_id}, State: {item['fields'].get('System.State', 'Unknown')})")
                break
    
    # Full history analysis
    potential_carryovers = []
    direct_moves = []
    
    for item_id in next_sprint_ids:
        print(f"\n--- Analyzing Item ID: {item_id} ---")
        
        # Find the item title for better logging
        item_title = "Unknown"
        for item in next_sprint_items:
            if item['id'] == item_id:
                item_title = item['fields'].get('System.Title', 'No Title')
                break
                
        print(f"Item: {item_title}")
        
        history = get_work_item_history(item_id)
        print(f"Found {len(history)} history records")
        
        was_in_current_sprint = False
        moved_to_next_sprint = False
        
        for update_idx, update in enumerate(history):
            print(f"\nUpdate {update_idx+1}:")
            update_date = parse_azure_date(update.get('revisedDate', ''))
            print(f"  Date: {update_date}")
            
            if 'fields' in update and 'System.IterationPath' in update['fields']:
                old_value = update['fields']['System.IterationPath'].get('oldValue', '')
                new_value = update['fields']['System.IterationPath'].get('newValue', '')
                print(f"  Iteration Change: {old_value} -> {new_value}")
                
                if old_value == current_iteration_path:
                    was_in_current_sprint = True
                    print(f"  Was in current sprint")
                    
                    if new_value == next_iteration_path:
                        moved_to_next_sprint = True
                        print(f"  Direct move to next sprint detected!")
                        direct_moves.append({
                            'id': item_id,
                            'title': item_title,
                            'update_date': update_date,
                            'during_sprint': current_sprint_start <= update_date <= current_sprint_end if update_date and current_sprint_start and current_sprint_end else "Unknown"
                        })
            
            if 'fields' in update and 'System.State' in update['fields']:
                old_state = update['fields']['System.State'].get('oldValue', '')
                new_state = update['fields']['System.State'].get('newValue', '')
                print(f"  State Change: {old_state} -> {new_state}")
        
        if was_in_current_sprint:
            potential_carryovers.append({
                'id': item_id,
                'title': item_title,
                'direct_move': moved_to_next_sprint
            })
            print(f"  Added to potential carryovers (direct_move={moved_to_next_sprint})")
    
    print("\n=== SUMMARY ===")
    print(f"Total items in Sprint {current_sprint.split()[-1]}: {len(current_sprint_items)}")
    print(f"Total items in Sprint {next_sprint.split()[-1]}: {len(next_sprint_items)}")
    print(f"Items in both sprints: {len(common_items)}")
    print(f"Potential carryovers: {len(potential_carryovers)}")
    print(f"Direct moves from current to next sprint: {len(direct_moves)}")
    
    print("\nDirect moves details:")
    for move in direct_moves:
        print(f"  - {move['title']} (ID: {move['id']})")
        print(f"    Moved on: {move['update_date']}")
        print(f"    During sprint: {move['during_sprint']}")
    
    print("\nPotential carryovers:")
    for item in potential_carryovers:
        print(f"  - {item['title']} (ID: {item['id']}, Direct move: {item['direct_move']})")
    
    return potential_carryovers

def main():
    print("=== SPRINT CARRYOVER DEBUGGING SCRIPT ===")
    
    # Get iteration data
    print("\nFetching iteration data...")
    iterations = get_sprint_iterations_data()
    print(f"Found {len(iterations)} iterations")
    
    # Get current sprint path
    current_iteration_path = None
    next_iteration_path = None
    
    for iteration in iterations:
        if iteration['name'] == current_sprint:
            current_iteration_path = iteration.get('path', '')
            print(f"Current Sprint Path: {current_iteration_path}")
            sprint_start, sprint_end = get_sprint_dates(iterations, current_sprint)
            print(f"Current Sprint Dates: {sprint_start} to {sprint_end}")
        elif iteration['name'] == next_sprint:
            next_iteration_path = iteration.get('path', '')
            print(f"Next Sprint Path: {next_iteration_path}")
    
    if not current_iteration_path or not next_iteration_path:
        print("Error: Could not find sprint paths")
        return
    
    # Get work items for both sprints
    print(f"\nFetching work items for {current_sprint}...")
    current_sprint_items = get_work_items_by_iteration_path(current_iteration_path)
    print(f"Found {len(current_sprint_items)} work items in {current_sprint}")
    
    print(f"\nFetching work items for {next_sprint}...")
    next_sprint_items = get_work_items_by_iteration_path(next_iteration_path)
    print(f"Found {len(next_sprint_items)} work items in {next_sprint}")
    
    # Debug carryover stories
    print("\n=== ANALYZING CARRYOVER STORIES ===")
    potential_carryovers = debug_carryover_stories(current_sprint_items, next_sprint_items, iterations)
    
    # Save detailed information to files for further analysis
    output_folder = "sprint_debug"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Save basic work item info for both sprints
    with open(f"{output_folder}/sprint70_items.json", 'w') as f:
        items_basic = []
        for item in current_sprint_items:
            items_basic.append({
                'id': item['id'],
                'title': item['fields'].get('System.Title', 'No Title'),
                'type': item['fields'].get('System.WorkItemType', 'Unknown'),
                'state': item['fields'].get('System.State', 'Unknown'),
                'points': item['fields'].get('Microsoft.VSTS.Scheduling.StoryPoints', 0)
            })
        json.dump(items_basic, f, indent=2)
    
    with open(f"{output_folder}/sprint71_items.json", 'w') as f:
        items_basic = []
        for item in next_sprint_items:
            items_basic.append({
                'id': item['id'],
                'title': item['fields'].get('System.Title', 'No Title'),
                'type': item['fields'].get('System.WorkItemType', 'Unknown'),
                'state': item['fields'].get('System.State', 'Unknown'),
                'points': item['fields'].get('Microsoft.VSTS.Scheduling.StoryPoints', 0)
            })
        json.dump(items_basic, f, indent=2)
    
    # Save potential carryovers
    with open(f"{output_folder}/potential_carryovers.json", 'w') as f:
        json.dump(potential_carryovers, f, indent=2)
    
    print(f"\nDebug information saved to {output_folder} folder")
    print("Please provide the actual list of carryover stories to compare with the detection results")

if __name__ == "__main__":
    main()
