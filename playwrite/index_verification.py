"""
Module for verifying the index structure built during tests.
"""

from node_utils import find_node_by_term, find_child_node_by_term, verify_page_numbers

def verify_index_structure(page, index_tracker):
    """
    Verify that the index structure in the UI matches our tracking data.
    
    Args:
        page: Playwright page object
        index_tracker: Instance of IndexTracking class
        
    Returns:
        bool: True if verification succeeds, False otherwise
    """
    print("\n=== VERIFYING INDEX STRUCTURE ===")
    
    # We'll verify only the structure we've built during this test
    # First, look for our primary term
    primary_term = index_tracker.structure[-1]["term"]  # Get the last primary term we added
    primary_pages = index_tracker.structure[-1]["page_numbers"]
    
    print(f"Looking for primary term: '{primary_term}'")
    
    # Find the node in the UI containing our primary term
    primary_node = find_node_by_term(page, primary_term, 1)
    
    if not primary_node:
        print(f"ERROR: Primary term '{primary_term}' not found in UI!")
        return False
    
    print(f"Found primary node in UI: '{primary_node['term']}'")
    
    # Verify primary node page numbers if any were added
    if primary_pages:
        verify_page_numbers(primary_node, primary_pages, 1)
    
    # Verify secondary nodes
    if index_tracker.structure[-1]["children"]:
        for secondary_tracking in index_tracker.structure[-1]["children"]:
            secondary_term = secondary_tracking["term"]
            secondary_pages = secondary_tracking["page_numbers"]
            
            print(f"Looking for secondary term: '{secondary_term}'")
            
            # Find matching secondary node that is a child of our primary node
            secondary_node = find_child_node_by_term(page, primary_node["element"], secondary_term, 2)
            
            if not secondary_node:
                print(f"ERROR: Secondary term '{secondary_term}' not found in UI!")
                continue
            
            print(f"Found secondary node in UI: '{secondary_node['term']}'")
            
            # Verify secondary node page numbers
            if secondary_pages:
                verify_page_numbers(secondary_node, secondary_pages, 2)
            
            # Verify tertiary nodes
            if secondary_tracking["children"]:
                for tertiary_tracking in secondary_tracking["children"]:
                    tertiary_term = tertiary_tracking["term"]
                    tertiary_pages = tertiary_tracking["page_numbers"]
                    
                    print(f"Looking for tertiary term: '{tertiary_term}'")
                    
                    # Find matching tertiary node that is a child of our secondary node
                    tertiary_node = find_child_node_by_term(page, secondary_node["element"], tertiary_term, 3)
                    
                    if not tertiary_node:
                        print(f"ERROR: Tertiary term '{tertiary_term}' not found in UI!")
                        continue
                    
                    print(f"Found tertiary node in UI: '{tertiary_node['term']}'")
                    
                    # Verify tertiary node page numbers
                    if tertiary_pages:
                        verify_page_numbers(tertiary_node, tertiary_pages, 3)
                    
                    # Verify quaternary nodes
                    if tertiary_tracking["children"]:
                        for quaternary_tracking in tertiary_tracking["children"]:
                            quaternary_term = quaternary_tracking["term"]
                            quaternary_pages = quaternary_tracking["page_numbers"]
                            
                            print(f"Looking for quaternary term: '{quaternary_term}'")
                            
                            # Find matching quaternary node that is a child of our tertiary node
                            quaternary_node = find_child_node_by_term(page, tertiary_node["element"], quaternary_term, 4)
                            
                            if not quaternary_node:
                                print(f"ERROR: Quaternary term '{quaternary_term}' not found in UI!")
                                continue
                            
                            print(f"Found quaternary node in UI: '{quaternary_node['term']}'")
                            
                            # Verify quaternary node page numbers
                            if quaternary_pages:
                                verify_page_numbers(quaternary_node, quaternary_pages, 4)
    
    print("=== VERIFICATION COMPLETE ===")
    return True
