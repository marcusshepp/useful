"""
Main test script for index builder testing.
"""

from playwright.sync_api import sync_playwright
from config import APP_URL
from index_tracker import IndexTracking
from navigation import login, navigate_to_index_builder
from index_builder_actions import test_index_builder_actions, test_quick_add_feature
from index_verification import verify_index_structure

def test_index_builder(playwright):
    """
    Run the index builder test including quick add feature.
    
    Args:
        playwright: Playwright instance
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    page.goto(APP_URL)
    
    # Initialize tracking structure
    index_tracker = IndexTracking()
    
    # Log in to the application
    login(page)
    
    # Navigate to the index builder page
    navigate_to_index_builder(page)
    
    # Test regular index builder actions
    # test_index_builder_actions(page, index_tracker)
    
    # Verify structure
    # verify_index_structure(page, index_tracker)
    
    # Test quick add feature
    test_quick_add_feature(page, index_tracker)
    
    # Verify structure again after quick add
    verify_index_structure(page, index_tracker)
    
    # Clean up
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        test_index_builder(playwright)
