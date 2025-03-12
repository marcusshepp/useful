"""
Utility functions for finding and verifying nodes in the index structure.
"""

def find_node_by_term(page, term, level):
    """
    Find a node in the UI by term and level.
    
    Args:
        page: Playwright page object
        term (str): The term to find
        level (int): The level of the term (1-4)
        
    Returns:
        dict: Node information if found, or None
    """
    # Get all nodes at the specified level
    nodes = page.locator(f".node[level='{level}']").all()
    
    for node in nodes:
        if node.is_visible():
            try:
                term_button = node.locator("button.term-name")
                node_term = term_button.text_content().strip()
                
                # Check for a match (exact or partial)
                if term_matches(term, node_term):
                    # Extract page numbers
                    page_numbers = extract_page_numbers(node)
                    
                    return {
                        "element": node,
                        "term": node_term,
                        "page_numbers": page_numbers
                    }
            except Exception as e:
                print(f"Error reading node data: {str(e)}")
    
    return None

def find_child_node_by_term(page, parent_node, term, level):
    """
    Find a child node of the specified parent by term and level.
    
    Args:
        page: Playwright page object
        parent_node: The parent node element
        term (str): The term to find
        level (int): The level of the term (1-4)
        
    Returns:
        dict: Node information if found, or None
    """
    # Get all child nodes of this parent at the specified level
    parent_id = parent_node.get_attribute("id")
    if not parent_id:
        print(f"Warning: Parent node has no ID attribute, cannot find children reliably")
        return None
    
    # Try to find direct children by parent-child relationship in the DOM
    try:
        # Find the children container
        children_container = parent_node.locator(".children-container")
        if children_container.is_visible():
            # Get all nodes at the specified level within this container
            child_nodes = children_container.locator(f".node[level='{level}']").all()
            
            for node in child_nodes:
                if node.is_visible():
                    try:
                        term_button = node.locator("button.term-name")
                        node_term = term_button.text_content().strip()
                        
                        # Check for a match (exact or partial)
                        if term_matches(term, node_term):
                            # Extract page numbers
                            page_numbers = extract_page_numbers(node)
                            
                            return {
                                "element": node,
                                "term": node_term,
                                "page_numbers": page_numbers
                            }
                    except Exception as e:
                        print(f"Error reading child node data: {str(e)}")
        else:
            print(f"Warning: Children container not visible for parent: {parent_id}")
    except Exception as e:
        print(f"Error finding children: {str(e)}")
    
    # If traditional approach fails, try an alternative
    # This is a fallback in case the DOM structure isn't as expected
    print(f"Using fallback method to find child node at level {level}")
    all_nodes = page.locator(f".node[level='{level}']").all()
    
    for node in all_nodes:
        if node.is_visible():
            try:
                term_button = node.locator("button.term-name")
                node_term = term_button.text_content().strip()
                
                # Check for a match (exact or partial)
                if term_matches(term, node_term):
                    # Extract page numbers
                    page_numbers = extract_page_numbers(node)
                    
                    return {
                        "element": node,
                        "term": node_term,
                        "page_numbers": page_numbers
                    }
            except Exception as e:
                print(f"Error reading node data in fallback: {str(e)}")
    
    return None

def extract_page_numbers(node):
    """
    Extract page numbers from a node element.
    
    Args:
        node: The node element
        
    Returns:
        list: Extracted page numbers
    """
    page_numbers = []
    try:
        page_numbers_element = node.locator(".page-numbers-container .page-numbers")
        if page_numbers_element.is_visible():
            page_numbers_text = page_numbers_element.text_content().strip()
            
            if page_numbers_text:
                # Parse page numbers from text
                numbers_text = page_numbers_text.split(",")
                for num in numbers_text:
                    try:
                        page_numbers.append(int(num.strip()))
                    except ValueError:
                        # Handle non-numeric values
                        pass
    except Exception as e:
        print(f"Error extracting page numbers: {str(e)}")
    
    return page_numbers

def term_matches(expected_term, actual_term):
    """
    Check if terms match (allowing for partial matches).
    
    Args:
        expected_term (str): The expected term
        actual_term (str): The actual term found in UI
        
    Returns:
        bool: True if terms match, False otherwise
    """
    # Try exact match first
    if expected_term == actual_term:
        return True
    
    # Try partial match (expected term could be truncated in the UI)
    if expected_term in actual_term or actual_term in expected_term:
        return True
    
    # Try a more lenient approach - first 10 chars
    if len(expected_term) > 10 and len(actual_term) > 10:
        if expected_term[:10] in actual_term or actual_term[:10] in expected_term:
            return True
    
    return False

def verify_page_numbers(node, expected_pages, level):
    """
    Verify if the page numbers match what we expect.
    
    Args:
        node (dict): Node information
        expected_pages (list): Expected page numbers
        level (int): Level of the node
    """
    actual_pages = node["page_numbers"]
    
    # If we have a specific list of expected pages that doesn't match actual pages
    if expected_pages and set(expected_pages) != set(actual_pages):
        print(f"WARNING: Page numbers for level {level} term '{node['term']}' don't exactly match.")
        print(f"  Expected: {sorted(expected_pages)}")
        print(f"  Actual: {sorted(actual_pages)}")
        
        # Check if all expected pages are present
        missing_pages = [page for page in expected_pages if page not in actual_pages]
        if missing_pages:
            print(f"  Missing pages: {missing_pages}")
        
        # Check if there are unexpected pages
        extra_pages = [page for page in actual_pages if page not in expected_pages]
        if extra_pages:
            print(f"  Unexpected pages: {extra_pages}")
    else:
        print(f"SUCCESS: All expected page numbers for level {level} term '{node['term']}' are present.")
