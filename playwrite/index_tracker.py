"""
Module for tracking index structure during test execution.
"""

class IndexTracking:
    """
    Class for tracking the hierarchical index structure being built during testing.
    """
    
    def __init__(self):
        """Initialize an empty index tracking structure."""
        self.structure = []
        self.current_primary = None
        self.current_secondary = None
        self.current_tertiary = None
        self.current_quaternary = None
    
    def add_primary(self, term, page_numbers=None):
        """
        Add a primary index term to the structure.
        
        Args:
            term (str): The term text
            page_numbers (list, optional): List of page numbers
            
        Returns:
            dict: The created node
        """
        node = {"term": term, "level": 1, "page_numbers": page_numbers or [], "children": []}
        self.structure.append(node)
        self.current_primary = node
        self.current_secondary = None
        self.current_tertiary = None
        self.current_quaternary = None
        return node
    
    def add_secondary(self, term, page_numbers=None):
        """
        Add a secondary index term to the current primary term.
        
        Args:
            term (str): The term text
            page_numbers (list, optional): List of page numbers
            
        Returns:
            dict: The created node or None if no primary term exists
        """
        if self.current_primary:
            node = {"term": term, "level": 2, "page_numbers": page_numbers or [], "children": []}
            self.current_primary["children"].append(node)
            self.current_secondary = node
            self.current_tertiary = None
            self.current_quaternary = None
            return node
        return None
    
    def add_tertiary(self, term, page_numbers=None):
        """
        Add a tertiary index term to the current secondary term.
        
        Args:
            term (str): The term text
            page_numbers (list, optional): List of page numbers
            
        Returns:
            dict: The created node or None if no secondary term exists
        """
        if self.current_secondary:
            node = {"term": term, "level": 3, "page_numbers": page_numbers or [], "children": []}
            self.current_secondary["children"].append(node)
            self.current_tertiary = node
            self.current_quaternary = None
            return node
        return None
    
    def add_quaternary(self, term, page_numbers=None):
        """
        Add a quaternary index term to the current tertiary term.
        
        Args:
            term (str): The term text
            page_numbers (list, optional): List of page numbers
            
        Returns:
            dict: The created node or None if no tertiary term exists
        """
        if self.current_tertiary:
            node = {"term": term, "level": 4, "page_numbers": page_numbers or [], "children": []}
            self.current_tertiary["children"].append(node)
            self.current_quaternary = node
            return node
        return None
    
    def add_page_numbers(self, level, page_numbers):
        """
        Add page numbers to a term at the specified level.
        
        Args:
            level (int): The level (1-4) to add page numbers to
            page_numbers (list): List of page numbers to add
        """
        if level == 1 and self.current_primary:
            self.current_primary["page_numbers"].extend(page_numbers)
        elif level == 2 and self.current_secondary:
            self.current_secondary["page_numbers"].extend(page_numbers)
        elif level == 3 and self.current_tertiary:
            self.current_tertiary["page_numbers"].extend(page_numbers)
        elif level == 4 and self.current_quaternary:
            self.current_quaternary["page_numbers"].extend(page_numbers)

    def print_structure(self):
        """Print the current index structure to console for debugging."""
        print("\n=== INDEX STRUCTURE ===")
        for primary in self.structure:
            print(f"Level 1: {primary['term']} - Pages: {primary['page_numbers']}")
            for secondary in primary["children"]:
                print(f"  Level 2: {secondary['term']} - Pages: {secondary['page_numbers']}")
                for tertiary in secondary["children"]:
                    print(f"    Level 3: {tertiary['term']} - Pages: {tertiary['page_numbers']}")
                    for quaternary in tertiary["children"]:
                        print(f"      Level 4: {quaternary['term']} - Pages: {quaternary['page_numbers']}")
        print("======================")
