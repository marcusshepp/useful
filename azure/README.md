# Azure DevOps Sprint Analysis Tool

This tool generates sprint performance reports and visualizations for Azure DevOps projects.

## Prerequisites

- Python 3.6+
- Azure DevOps personal access token with read access to work items

## Setup

1. Install required dependencies:

```
pip install requests matplotlib numpy
```

2. Set your Azure DevOps token as an environment variable:

```
export AZURE_TOKEN=your_azure_token_here
```

## Configuration

Edit the following variables in `main.py` to match your Azure DevOps setup:

- `organization`: Your Azure DevOps organization name
- `project`: Your project name
- `team`: Your team name
- `current_sprint`: The current sprint name (e.g., "Sprint 70")
- `sprint_range_start` and `sprint_range_end`: The range of sprint numbers to analyze

## Usage

### Basic Usage

Run the script without any arguments to generate reports for your configured sprints:

```
python main.py
```

### With Carry-over Items

If you have stories carried over from a previous sprint, you can account for them:

```
python main.py --cotickets 3 --copoints 15
```

Where:

- `--cotickets` is the number of user stories carried over
- `--copoints` is the number of story points carried over

## Output

The tool generates the following in a date-stamped folder under `sprint_reports/`:

- `sprintReport.txt`: A text summary of each sprint's metrics
- `velocity_graph.png`: 3-sprint rolling average velocity chart
- `bugs_graph.png`: Bugs completed per sprint
- `commitment_graph.png`: Comparison of committed vs. completed work
- `sprint_stats.png`: Current sprint statistics
- `rolling_average_graph.png`: 5-sprint rolling average performance

## Example

```
python main.py --cotickets 2 --copoints 8
```

This will generate all reports with adjustments for 2 carried-over user stories worth 8 points.
