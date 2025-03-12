# Index Builder Test Automation

This project contains automated tests for the Index Builder feature using Playwright with Python.

## Project Structure

- **main_test.py** - Main test runner script
- **config.py** - Configuration settings and test data
- **index_tracker.py** - Class for tracking the index structure during tests
- **navigation.py** - Helper functions for navigating the application
- **index_builder_actions.py** - Functions for interacting with the index builder
- **node_utils.py** - Utility functions for finding and manipulating nodes
- **index_verification.py** - Verification utilities for the index structure

## Prerequisites

- Python 3.8+
- Playwright for Python

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install playwright
playwright install
```

## Configuration

Modify `config.py` to adjust:

- Application URL
- Login credentials
- Test data (search terms)

## Running Tests

Execute the main test script:

```bash
python main_test.py
```

## Test Flow

1. Launch browser and navigate to the application
2. Log in using credentials from config
3. Navigate to the Index Builder page
4. Add a primary index term
5. Add a secondary term under the primary term
6. Add page numbers to the secondary term
7. Add a tertiary term under the secondary term
8. Add page numbers to the tertiary term
9. Add a quaternary term under the tertiary term
10. Add page numbers to the quaternary term
11. Verify the structure in the UI matches our tracking data

## Extending Tests

To add more test scenarios:

1. Create new functions in `index_builder_actions.py`
2. Update the `test_index_builder_actions` function to include the new scenarios
3. Add any necessary verification steps in `index_verification.py`

## Debugging

The test script includes detailed logging to help with debugging. If a test fails, check the console output for information on which step failed and why.
