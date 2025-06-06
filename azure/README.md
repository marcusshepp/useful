# Azure DevOps Sprint Analysis Tool

This tool generates sprint performance reports and visualizations for Azure DevOps projects.

## Prerequisites

- Python 3.6+
- Azure DevOps personal access token with read access to work items

## Setup

1. Install required dependencies:

```bash
pip install requests matplotlib numpy
```

2. Set your Azure DevOps token as an environment variable:

```bash
export AZURE_TOKEN=your_azure_token_here
```

## Configuration

Edit the following variables in `main.py` to match your Azure DevOps setup:

- `organization`: Your Azure DevOps organization name
- `project`: Your project name
- `team`: Your team name
- `current_sprint`: The current sprint name (e.g., "Sprint 77")
- `sprint_range_start` and `sprint_range_end`: The range of sprint numbers to analyze

## Usage

### Basic Usage

Run the script without any arguments to generate reports for your configured sprints:

```bash
python main.py
```

### With Carry-over Items

If you have stories carried over from a previous sprint, you can account for them:

```bash
python main.py --cotickets 3 --copoints 15
```

### Override Committed Values

Override the number of stories or points committed for a sprint (useful for manual adjustments):

```bash
python main.py --stories-committed 10 --points-committed 35.0
```

### Target Specific Sprint

Apply overrides to a specific sprint instead of the current one:

```bash
python main.py --sprint "Sprint 76" --stories-committed 8 --points-committed 28.0
```

### Combined Usage

Combine carry-over data with overrides:

```bash
python main.py --cotickets 1 --copoints 5 --stories-committed 9 --points-committed 31.0
```

## Command Line Arguments

| Argument              | Type  | Description                                                          |
| --------------------- | ----- | -------------------------------------------------------------------- |
| `--cotickets`         | int   | Number of user stories carried over from previous sprint             |
| `--copoints`          | int   | Number of story points carried over from previous sprint             |
| `--stories-committed` | int   | Override the number of stories committed for target sprint           |
| `--points-committed`  | float | Override the number of points committed for target sprint            |
| `--sprint`            | str   | Specify which sprint to apply overrides to (default: current sprint) |

## Data Persistence

The tool maintains two data files:

- `sprint_carryover_data.json`: Stores carry-over tickets and points for each sprint
- `sprint_override_data.json`: Stores manual overrides for committed stories and points

These files persist data across runs, so you don't need to re-enter the same adjustments.

## Output

The tool generates the following in a date-stamped folder under `sprint_reports/`:

- `sprintReport.txt`: A text summary of each sprint's metrics with override indicators
- `velocity_graph.png`: 3-sprint rolling average velocity chart
- `bugs_graph.png`: Bugs completed per sprint
- `commitment_graph.png`: Comparison of committed vs. completed work
- `sprint_stats.png`: Current sprint statistics
- `rolling_average_graph.png`: 5-sprint rolling average performance

## Examples

### Basic report generation:

```bash
python main.py
```

### Account for carry-over items:

```bash
python main.py --cotickets 2 --copoints 8
```

### Override current sprint commitments:

```bash
python main.py --stories-committed 12 --points-committed 40.5
```

### Apply adjustments to a previous sprint:

```bash
python main.py --sprint "Sprint 75" --cotickets 1 --copoints 3 --stories-committed 11
```

### Complex scenario with all adjustments:

```bash
python main.py --sprint "Sprint 77" --cotickets 1 --copoints 5 --stories-committed 9 --points-committed 31.0
```

This will:

- Target Sprint 77
- Add 1 carry-over ticket and 5 carry-over points
- Override committed stories to 9
- Override committed points to 31.0

## Notes

- Overrides are applied after fetching data from Azure DevOps
- The tool will display when overrides are being applied during execution
- Sprint reports clearly indicate when overrides have been used
- All adjustments are saved and persist across multiple runs
