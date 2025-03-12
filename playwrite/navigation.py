"""
Module for navigating through the application in tests.
"""

import time
from playwright.sync_api import expect
from config import USERNAME, PASSWORD

def login(page):
    """
    Login to the application.
    
    Args:
        page: Playwright page object
    """
    page.wait_for_selector("form mat-card", timeout=10000)
    print("Found login form")
    
    username_input = page.locator("input[matinput][id='mat-input-0']")
    username_input.fill(USERNAME)
    print(f"Found and filled username input with: {USERNAME}")
    
    password_input = page.locator("input[type='password'][id='mat-input-1']")
    password_input.fill(PASSWORD)
    print(f"Found and filled password input")
    
    login_button = page.locator("button:has-text('Login')")
    login_button.click()
    print("Found and clicked Login button")
    
    page.wait_for_load_state("networkidle", timeout=10000)

def navigate_to_index_builder(page):
    """
    Navigate to the index builder page from the main dashboard.
    
    Args:
        page: Playwright page object
    """
    page.wait_for_selector(".mi-content-header", timeout=10000)
    print("Found content header")
    
    hamburger_menu = page.locator("#mi-sidebar-toggle")
    hamburger_menu.click()
    print("Found and clicked hamburger menu")
    
    page.wait_for_timeout(1000)
    
    official_journal_menu = page.locator("div.side-navigation-item:has-text('Official Journal')")
    official_journal_menu.click()
    print("Found and clicked Official Journal menu")
    
    page.wait_for_timeout(1000)
    
    general_index_link = page.locator("span.submenu-name:has-text('General Index Builder')")
    general_index_link.click()
    print("Found and clicked General Index Builder link")
    
    page.wait_for_selector(".index-builder-container", timeout=10000)
    print("Index builder container loaded")
    
    # Close the sidenav by clicking the hamburger menu again
    hamburger_menu = page.locator("#mi-sidebar-toggle")
    hamburger_menu.click()
    print("Closed sidebar via hamburger menu")
