"""
Module for interacting with the index builder interface.
"""

import time
import random
from playwright.sync_api import expect
from config import SEARCH_TERMS
from node_utils import find_node_by_term, find_child_node_by_term, verify_page_numbers

def test_index_builder_actions(page, index_tracker):
    """
    Test various actions in the index builder interface.
    
    Args:
        page: Playwright page object
        index_tracker: Instance of IndexTracking class
    """
    expect(page.locator(".index-builder-container")).to_be_visible()
    print("Index builder container is visible")
    
    # Add primary index
    add_primary_index_btn = page.locator("button:has-text('Add Primary Index')")
    expect(add_primary_index_btn).to_be_enabled()
    add_primary_index_btn.click()
    print("Found and clicked Add Primary Index button")
    
    page.wait_for_selector("input[placeholder='Search']", timeout=5000)
    print("Search input is visible")
    
    # Select a random search term from the list
    primary_term = random.choice(SEARCH_TERMS)
    
    search_input = page.locator("input[placeholder='Search']")
    search_input.fill(primary_term)
    print(f"Found and filled search input with: {primary_term}")
    
    # Wait for autocomplete panel to appear
    page.wait_for_selector("div.mat-autocomplete-panel", timeout=5000)
    print("Autocomplete panel is visible")
    
    # Wait a moment for the options to populate
    time.sleep(1)
    
    # Track the primary term we're adding
    selected_primary_term = primary_term
    
    # Select the first autocomplete option
    try:
        first_option = page.locator("mat-option").first
        if first_option.is_visible():
            selected_text = first_option.text_content().strip()
            if selected_text:
                selected_primary_term = selected_text
            first_option.click()
            print(f"Found and clicked first autocomplete option: {selected_primary_term}")
        else:
            # Try alternative selector if the first approach doesn't work
            option = page.locator("mat-option .mat-option-text").first
            selected_text = option.text_content().strip()
            if selected_text:
                selected_primary_term = selected_text
            option.click()
            print(f"Found and clicked first autocomplete option for: {selected_primary_term}")
    except:
        print("Could not find an autocomplete option, trying direct entry")
        search_input.press("Enter")
    
    # Add primary node to tracking
    primary_node = index_tracker.add_primary(selected_primary_term)
    
    time.sleep(2)
    
    # Find the newly added primary node in the tree
    try:
        # Try looking for the exact term first
        node_button = page.locator(f"button.term-name:has-text('{selected_primary_term}')").first
        if not node_button.is_visible():
            # If exact term not found, try a partial match approach
            all_nodes = page.locator("button.term-name")
            count = all_nodes.count()
            found = False
            for i in range(count):
                node = all_nodes.nth(i)
                if node.is_visible():
                    node_text = node.text_content().strip()
                    print(f"Found node: {node_text}")
                    # Update our tracking with the actual text content if different
                    if node_text != selected_primary_term:
                        primary_node["term"] = node_text
                        selected_primary_term = node_text
                    node_button = node
                    found = True
                    break
            
            if not found:
                # If still not found, just take the first node we can find
                node_button = page.locator("button.term-name").first
                node_text = node_button.text_content().strip()
                print(f"Using first available node: {node_text}")
                # Update tracking
                primary_node["term"] = node_text
                selected_primary_term = node_text
        
        # Click on the add child term button next to our node
        parent_node = node_button.locator("xpath=../..")  # Go to the parent div
        add_child_btn = parent_node.locator("i.fa-plus")
        add_child_btn.click()
        print(f"Clicked add child button for node: {selected_primary_term}")
        
        # Now add a secondary term
        time.sleep(0.3)
        page.wait_for_selector("input[placeholder='Search']", timeout=5000)
        
        # Choose a different random search term
        secondary_term = random.choice([term for term in SEARCH_TERMS if term != selected_primary_term])
        
        search_input = page.locator("input[placeholder='Search']")
        search_input.fill(secondary_term)
        print(f"Found and filled search input with secondary term: {secondary_term}")
        
        # Track the secondary term
        selected_secondary_term = secondary_term
        
        # Wait for autocomplete panel
        page.wait_for_selector("div.mat-autocomplete-panel", timeout=5000)
        time.sleep(1)
        
        # Select the first autocomplete option for secondary term
        try:
            first_option = page.locator("mat-option").first
            if first_option.is_visible():
                selected_text = first_option.text_content().strip()
                if selected_text:
                    selected_secondary_term = selected_text
                first_option.click()
                print(f"Found and clicked first autocomplete option for secondary term: {selected_secondary_term}")
            else:
                option = page.locator("mat-option .mat-option-text").first
                selected_text = option.text_content().strip()
                if selected_text:
                    selected_secondary_term = selected_text
                option.click()
                print(f"Found and clicked first autocomplete option for secondary term: {selected_secondary_term}")
        except:
            print("Could not find an autocomplete option for secondary term, trying direct entry")
            search_input.press("Enter")
        
        # Add secondary node to tracking
        secondary_node = index_tracker.add_secondary(selected_secondary_term)
        
        time.sleep(2)
        print("Added secondary node successfully")
    
    except Exception as e:
        print(f"Error adding secondary node: {str(e)}")
    
    # Add random page numbers to the secondary node
    try:
        # Find the newly added secondary node
        time.sleep(0.3)
        secondary_nodes = page.locator("button.term-name:has-text('" + selected_secondary_term[:10] + "')").all()
        secondary_node = None
        
        if len(secondary_nodes) > 0:
            # Find the page numbers container next to the secondary node
            for node in secondary_nodes:
                if node.is_visible():
                    secondary_node = node
                    print(f"Found secondary node: {secondary_node.text_content().strip()}")
                    add_random_page_numbers(page, secondary_node, 2, index_tracker)
                    break
        
        # Now add a third level node
        if secondary_node:
            third_node = add_child_node(page, secondary_node, 2, index_tracker)
            if third_node:
                # Add page numbers to the third level node
                add_random_page_numbers(page, third_node, 3, index_tracker)
                
                # Add a fourth level node
                fourth_node = add_child_node(page, third_node, 3, index_tracker)
                if fourth_node:
                    # Add page numbers to the fourth level node
                    add_random_page_numbers(page, fourth_node, 4, index_tracker)
    
    except Exception as e:
        print(f"Error in node creation process: {str(e)}")
        
    # Check journal status
    journal_status = page.locator("button:has-text('Journal Document Unpublished')")
    if journal_status.is_visible():
        expect(journal_status).to_be_disabled()
        print("Found Journal Document Unpublished button (disabled)")
    else:
        print("Journal Document Unpublished button not found")
    
    # Print the structure we've built
    index_tracker.print_structure()

def add_random_page_numbers(page, node, level, index_tracker):
    """
    Add random page numbers to a node.
    
    Args:
        page: Playwright page object
        node: The node element
        level (int): The level of the node (1-4)
        index_tracker: Instance of IndexTracking class
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        parent_node = node.locator("xpath=../..")
        page_numbers_container = parent_node.locator(".page-numbers-container")
        if page_numbers_container.is_visible():
            # Click on the page numbers container to open the dialog
            page_numbers_container.click()
            print(f"Clicked page numbers container to open dialog for {node.text_content().strip()}")
            
            # Wait for the dialog to appear
            page.wait_for_selector("mat-card.dialog-container", timeout=5000)
            print("Page numbers dialog appeared")
            
            # Generate a random number of page numbers to add (between 5-10)
            num_pages_to_add = random.randint(5, 10)
            print(f"Will add {num_pages_to_add} random page numbers")
            
            added_page_numbers = []
            
            # Add random page numbers
            for i in range(num_pages_to_add):
                # Generate a random page number between 1 and 999
                page_number = random.randint(1, 999)
                
                # Fill in the page number input
                page_number_input = page.locator("input[type='number'][matinput]")
                page_number_input.fill(str(page_number))
                
                # Click the Add button
                add_button = page.locator(".top-row-button button:has-text('Add')")
                add_button.click()
                print(f"Added page number: {page_number}")
                
                # Add to tracking
                added_page_numbers.append(page_number)
                
                # Brief pause to ensure the page number is added
                time.sleep(0.1)
            
            # Close the dialog
            close_button = page.locator("button:has-text('Close')")
            close_button.click()
            print("Closed page numbers dialog")
            time.sleep(0.2)
            
            # Update tracking with the page numbers added
            index_tracker.add_page_numbers(level, added_page_numbers)
            
            return True
    except Exception as e:
        print(f"Error adding page numbers: {str(e)}")
    return False

def add_child_node(page, parent_node, level, index_tracker):
    """
    Add a child node to a parent node.
    
    Args:
        page: Playwright page object
        parent_node: The parent node element
        level (int): The level of the parent node (1-3)
        index_tracker: Instance of IndexTracking class
        
    Returns:
        node: The created child node element or None if failed
    """
    try:
        # Click on the add child term button next to the parent node
        parent_container = parent_node.locator("xpath=../..")
        add_child_btn = parent_container.locator("i.fa-plus")
        if add_child_btn.is_visible():
            add_child_btn.click()
            print(f"Clicked add child button for level {level} node: {parent_node.text_content().strip()}")
            
            # Now add a child term
            time.sleep(0.3)
            page.wait_for_selector("input[placeholder='Search']", timeout=5000)
            
            # Choose a random search term
            child_term = random.choice(SEARCH_TERMS)
            
            search_input = page.locator("input[placeholder='Search']")
            search_input.fill(child_term)
            print(f"Found and filled search input with level {level+1} term: {child_term}")
            
            # Track the term we're adding
            selected_child_term = child_term
            
            # Wait for autocomplete panel
            page.wait_for_selector("div.mat-autocomplete-panel", timeout=5000)
            time.sleep(0.3)
            
            # Select the first autocomplete option
            try:
                first_option = page.locator("mat-option").first
                if first_option.is_visible():
                    selected_text = first_option.text_content().strip()
                    if selected_text:
                        selected_child_term = selected_text
                    first_option.click()
                    print(f"Found and clicked first autocomplete option for level {level+1} term: {selected_child_term}")
                else:
                    option = page.locator("mat-option .mat-option-text").first
                    selected_text = option.text_content().strip()
                    if selected_text:
                        selected_child_term = selected_text
                    option.click()
                    print(f"Found and clicked first autocomplete option for level {level+1} term: {selected_child_term}")
            except:
                print(f"Could not find an autocomplete option for level {level+1} term, trying direct entry")
                search_input.press("Enter")
            
            # Add node to tracking based on level
            if level == 2:
                child_node_tracking = index_tracker.add_tertiary(selected_child_term)
            elif level == 3:
                child_node_tracking = index_tracker.add_quaternary(selected_child_term)
            
            time.sleep(1)
            
            # Find the newly added child node - using a more reliable method
            child_nodes = page.locator(f".node[level='{level+1}'] button.term-name").all()
            latest_nodes = []
            for node in child_nodes:
                if node.is_visible():
                    latest_nodes.append(node)
            
            if latest_nodes:
                child_node = latest_nodes[-1]  # Get the last visible node at this level
                node_text = child_node.text_content().strip()
                print(f"Found level {level+1} node: {node_text}")
                
                # Update tracking if actual text is different
                if node_text != selected_child_term:
                    if level == 2:
                        index_tracker.current_tertiary["term"] = node_text
                    elif level == 3:
                        index_tracker.current_quaternary["term"] = node_text
                
                return child_node
    except Exception as e:
        print(f"Error adding level {level+1} node: {str(e)}")
    return None


def test_quick_add_feature(page, index_tracker):
    """
    Test the quick add dialog feature in the index builder interface.
    
    Args:
        page: Playwright page object
        index_tracker: Instance of IndexTracking class
    """
    expect(page.locator(".index-builder-container")).to_be_visible()
    print("Index builder container is visible")
    
    # Find and click the quick add button
    quick_add_btn = page.locator("button:has-text('Quick Add')")  # Adjust selector if needed
    expect(quick_add_btn).to_be_enabled()
    quick_add_btn.click()
    print("Found and clicked Quick Add button")
    
    # Wait for the quick add dialog to appear
    page.wait_for_selector(".quick-add-container", timeout=5000)
    print("Quick add dialog is visible")
    
    # Test adding a primary term
    primary_term = random.choice(SEARCH_TERMS)
    search_input = page.locator("input[placeholder='Type to search...']")
    search_input.fill(primary_term)
    print(f"Filled search input with primary term: {primary_term}")
    
    # Wait for autocomplete or add option with more flexibility
    selected_primary_term = primary_term
    try:
        # Increase timeout and check visibility more carefully
        page.wait_for_selector("mat-autocomplete", timeout=10000, state="visible")
        print("Autocomplete panel is visible")
        time.sleep(1)  # Give it a moment to populate options
        
        first_option = page.locator("mat-option").first
        if first_option.is_visible():
            selected_text = first_option.text_content().strip()
            if selected_text:
                selected_primary_term = selected_text
            first_option.click()
            print(f"Selected autocomplete option: {selected_primary_term}")
        else:
            add_option = page.locator("mat-option.add-term-option")
            if add_option.is_visible():
                selected_text = add_option.text_content().strip()
                if selected_text:
                    selected_primary_term = selected_text.split('"')[1]  # Extract term from "Add new term: ..."
                add_option.click()
                print(f"Added new term: {selected_primary_term}")
            else:
                print("No autocomplete options visible, pressing Enter")
                search_input.press("Enter")
    except Exception as e:
        print(f"Autocomplete wait failed: {str(e)}")
        print("Attempting to proceed by pressing Enter")
        search_input.press("Enter")
        time.sleep(1)  # Give it a moment to process
    
    # Track the primary term
    primary_node = index_tracker.add_primary(selected_primary_term)
    
    # Wait for secondary level input
    try:
        page.wait_for_selector("input[placeholder='Type to search...']", timeout=5000)
        print("Secondary level search input is visible")
    except Exception as e:
        print(f"Failed to find secondary input: {str(e)}")
        return  # Exit if we can't proceed
    
    # Test adding a secondary term
    secondary_term = random.choice([term for term in SEARCH_TERMS if term != selected_primary_term])
    search_input.fill(secondary_term)
    print(f"Filled search input with secondary term: {secondary_term}")
    
    selected_secondary_term = secondary_term
    try:
        page.wait_for_selector("mat-autocomplete", timeout=10000, state="visible")
        time.sleep(1)
        
        first_option = page.locator("mat-option").first
        if first_option.is_visible():
            selected_text = first_option.text_content().strip()
            if selected_text:
                selected_secondary_term = selected_text
            first_option.click()
            print(f"Selected autocomplete option for secondary: {selected_secondary_term}")
        else:
            add_option = page.locator("mat-option.add-term-option")
            if add_option.is_visible():
                selected_text = add_option.text_content().strip()
                if selected_text:
                    selected_secondary_term = selected_text.split('"')[1]
                add_option.click()
                print(f"Added new secondary term: {selected_secondary_term}")
            else:
                print("No autocomplete options visible for secondary, pressing Enter")
                search_input.press("Enter")
    except Exception as e:
        print(f"Secondary autocomplete wait failed: {str(e)}")
        search_input.press("Enter")
    
    # Track the secondary term
    secondary_node = index_tracker.add_secondary(selected_secondary_term)
    
    # Wait for page numbers input
    try:
        page.wait_for_selector("input[placeholder='Enter page number']", timeout=5000)
        print("Page numbers input is visible")
    except Exception as e:
        print(f"Failed to find page numbers input: {str(e)}")
        return
    
    # Add some random page numbers
    page_number_input = page.locator("input[type='number'][matinput]")
    num_pages = random.randint(2, 5)
    added_page_numbers = []
    
    for _ in range(num_pages):
        page_number = random.randint(1, 999)
        page_number_input.fill(str(page_number))
        page_number_input.press("Enter")
        added_page_numbers.append(page_number)
        print(f"Added page number: {page_number}")
        time.sleep(0.3)
    
    # Track page numbers
    index_tracker.add_page_numbers(2, added_page_numbers)
    
    # Test removing a page number
    if added_page_numbers:
        page_to_remove = added_page_numbers[0]
        remove_btn = page.locator(f".page-number-item:has-text('{page_to_remove}') i.fa-trash")
        if remove_btn.is_visible():
            remove_btn.click()
            print(f"Removed page number: {page_to_remove}")
            index_tracker.current_secondary["page_numbers"] = [
                pn for pn in index_tracker.current_secondary["page_numbers"] if pn != page_to_remove
            ]
        else:
            print(f"Could not find remove button for page number: {page_to_remove}")
    
    # Finish page numbers and move to tertiary
    page.keyboard.press("Tab")
    time.sleep(1)
    
    # Add tertiary term
    try:
        page.wait_for_selector("input[placeholder='Type to search...']", timeout=5000)
        tertiary_term = random.choice([term for term in SEARCH_TERMS if term not in [selected_primary_term, selected_secondary_term]])
        search_input.fill(tertiary_term)
        search_input.press("Enter")
        index_tracker.add_tertiary(tertiary_term)
        print(f"Added tertiary term: {tertiary_term}")
    except Exception as e:
        print(f"Failed to add tertiary term: {str(e)}")
    
    # Close the dialog
    close_btn = page.locator("button:has-text('Close')")
    close_btn.click()
    print("Closed quick add dialog")
    
    time.sleep(2)
    index_tracker.print_structure()
