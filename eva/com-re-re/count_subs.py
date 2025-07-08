#!/usr/bin/env python3
import json
import sys
import os

def count_non_null_sub_values(json_file_path: str) -> None:
    if not os.path.exists(json_file_path):
        print(f"Error: File {json_file_path} not found")
        sys.exit(1)
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        action_to_agenda_items = data.get("action_to_agenda_items", [])
        
        total_items = len(action_to_agenda_items)
        items_with_sub_key = 0
        items_with_non_null_sub = 0
        
        for item in action_to_agenda_items:
            if "Sub" in item:
                items_with_sub_key += 1
                sub_value = item.get("Sub")
                if sub_value is not None and sub_value != "":
                    items_with_non_null_sub += 1
        
        print(f"Total action_to_agenda_items: {total_items}")
        print(f"Items with 'Sub' key: {items_with_sub_key}")
        print(f"Items with non-null/non-empty 'Sub' value: {items_with_non_null_sub}")
        print(f"Percentage with non-null Sub: {(items_with_non_null_sub/total_items*100):.2f}%" if total_items > 0 else "No items found")
        
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    json_file_path = "uat_data/migration_data.json"
    count_non_null_sub_values(json_file_path)
