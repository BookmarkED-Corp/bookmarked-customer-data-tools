# Kanban Board Implementation Prompt

Implement a folder-based Kanban board system for managing development tasks in this project. The system should be optimized for AI agent workflows and git-friendly collaboration.

## Overview

Create a command-line Kanban board that:
- Stores each task as an individual JSON file in column-specific folders
- Provides a rich CLI interface for task management
- Supports AI agent and human developer workflows
- Is fully git-friendly (no merge conflicts on concurrent work)
- Includes comprehensive task metadata and validation

## Directory Structure

Create the following structure in the project root:

```
kanban/
├── README.md              # Comprehensive documentation
├── board-metadata.json    # Board configuration
├── kanban.py             # CLI tool (executable)
├── backlog/              # Tasks to be done
├── ready/                # Tasks ready to work on
├── in_progress/          # Tasks being worked on
├── review/               # Tasks awaiting validation
└── done/                 # Completed tasks
```

## Dependencies

Install these Python packages:
```
click==8.1.7    # CLI framework
rich==13.7.0    # Terminal formatting and tables
```

## File Specifications

### 1. board-metadata.json

```json
{
  "board_info": {
    "name": "[PROJECT_NAME] Development",
    "created": "YYYY-MM-DD",
    "version": "2.0.0",
    "system": "folder-based",
    "description": "[PROJECT DESCRIPTION]"
  },
  "columns": {
    "backlog": {
      "name": "Backlog",
      "description": "Tasks that need to be done",
      "order": 1
    },
    "ready": {
      "name": "Ready",
      "description": "Tasks ready to be worked on",
      "order": 2
    },
    "in_progress": {
      "name": "In Progress",
      "description": "Tasks currently being worked on",
      "order": 3
    },
    "review": {
      "name": "Review",
      "description": "Tasks awaiting review/validation",
      "order": 4
    },
    "done": {
      "name": "Done",
      "description": "Completed tasks",
      "order": 5
    }
  },
  "task_template": {
    "id": "TASK-000",
    "title": "",
    "description": "",
    "type": "feature|bug|test|docs|refactor",
    "priority": "low|medium|high|critical",
    "assignee": "agent|human|unassigned",
    "use_case": "",
    "test_data": {
      "good_samples": [],
      "bad_samples": []
    },
    "acceptance_criteria": [],
    "validation_status": "pending|passed|failed",
    "created_at": "",
    "updated_at": "",
    "completed_at": null,
    "tags": [],
    "notes": []
  },
  "next_task_number": 1
}
```

### 2. kanban.py - CLI Tool

Create a Python CLI tool with these features:

**Core Functions:**
- `load_metadata()` - Load board metadata
- `save_metadata(metadata)` - Save board metadata
- `load_task(task_file)` - Load individual task
- `save_task(task, column)` - Save task to column folder
- `get_all_tasks()` - Get all tasks organized by column
- `find_task(task_id)` - Find task and its location
- `generate_task_id()` - Generate next task ID

**Commands to implement:**

1. **show** - Display the kanban board
   - Options: `--column` (show specific column)
   - Display as rich tables with columns: ID, Title, Type, Priority, Assignee
   - Color-coded output

2. **add** - Add new task
   - Interactive mode (prompts for all fields)
   - Options: `--title`, `--description`, `--type`, `--priority`, `--use-case`, `--assignee`
   - Task types: feature, bug, test, docs, refactor
   - Priority levels: low, medium, high, critical
   - Assignees: agent, human, unassigned
   - Creates task in backlog folder

3. **move** - Move task between columns
   - Arguments: `task_id`, `column`
   - Updates `updated_at` timestamp
   - Sets `completed_at` and `validation_status=passed` when moving to done
   - Moves file physically between folders

4. **assign** - Assign task to agent or human
   - Arguments: `task_id`, `assignee` (agent|human|unassigned)
   - Updates task assignee field

5. **details** - Show detailed task information
   - Argument: `task_id`
   - Display all task fields in formatted output
   - Show: description, current column, metadata, acceptance criteria, test data, tags, notes

6. **stats** - Show board statistics
   - Display table with counts per column
   - Break down by priority and assignee
   - Show total task count

7. **update** - Update task properties
   - Argument: `task_id`
   - Options: `--title`, `--description`, `--priority`, `--type`, `--add-note`, `--add-tag`
   - Notes include timestamp when added

8. **delete** - Delete task permanently
   - Argument: `task_id`
   - Requires confirmation prompt

9. **list-files** - List all task files (debugging)
   - Show task files organized by column

**CLI Structure:**
```python
#!/usr/bin/env python3
import json
import click
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()
KANBAN_DIR = Path(__file__).parent
METADATA_FILE = KANBAN_DIR / "board-metadata.json"
COLUMNS = ['backlog', 'ready', 'in_progress', 'review', 'done']

@click.group()
def cli():
    """Kanban board management for [PROJECT_NAME]"""
    pass

# Implement all commands here...

if __name__ == '__main__':
    cli()
```

### 3. Task File Format (TASK-XXX.json)

Each task should be stored as:

```json
{
  "id": "TASK-001",
  "title": "Implement feature X",
  "description": "Detailed description of what needs to be done",
  "type": "feature",
  "priority": "high",
  "assignee": "agent",
  "use_case": "UC-001",
  "test_data": {
    "good_samples": ["data/samples/valid.json"],
    "bad_samples": ["data/samples/invalid.json"]
  },
  "acceptance_criteria": [
    "Feature works as expected",
    "Tests pass",
    "Documentation updated"
  ],
  "validation_status": "pending",
  "created_at": "2025-10-12T10:00:00",
  "updated_at": "2025-10-12T10:00:00",
  "completed_at": null,
  "tags": ["backend", "api"],
  "notes": []
}
```

### 4. README.md

Create comprehensive documentation covering:

1. **Directory Structure** - Visual representation
2. **Why Folder-Based?** - Benefits (git-friendly, parallel work, scalability)
3. **Usage Examples** - All commands with examples
4. **Task Types and Priority Levels** - Definitions
5. **Workflow for AI Agents** - Step-by-step process
6. **Workflow for Human Developers** - Step-by-step process
7. **Best Practices** - Creating, working on, and reviewing tasks
8. **Git Integration** - How to commit task changes
9. **Troubleshooting** - Common issues and solutions
10. **Advanced Usage** - Bulk operations, custom queries with jq

## Integration Setup

### Option 1: Simple Activation Script

Create `activate.sh` in project root:
```bash
#!/bin/bash
# Activate virtual environment and run kanban CLI

source venv/bin/activate
python kanban/kanban.py "$@"
```

Usage: `./activate.sh kanban show`

### Option 2: Command Center Integration

If you have a main CLI tool (like `command_center.py`), add kanban commands as a group:

```python
@cli.group()
def kanban():
    """Kanban board commands"""
    pass

@kanban.command()
def show():
    """Show kanban board"""
    subprocess.run("python kanban/kanban.py show", shell=True)

@kanban.command()
def add():
    """Add new task"""
    subprocess.run("python kanban/kanban.py add", shell=True)

# Add other commands...
```

## Key Features to Implement

1. **Git-Friendly Design**
   - Each task is a separate file
   - Moving tasks = moving files (clear git history)
   - No merge conflicts on parallel work

2. **Rich Terminal Output**
   - Use `rich.table.Table` for board display
   - Color-coded status (green for success, red for errors, yellow for warnings)
   - Clear, readable formatting

3. **Metadata Tracking**
   - Auto-generate task IDs (TASK-001, TASK-002, etc.)
   - Track creation, update, and completion timestamps
   - Maintain board metadata separately

4. **Validation**
   - Check for required fields
   - Validate task IDs
   - Handle missing files gracefully
   - Provide clear error messages

5. **Search and Filter**
   - Show specific columns
   - Filter by assignee, priority, or type
   - Statistics and reporting

## Workflow Examples

### AI Agent Workflow

```bash
# 1. Check available tasks
./activate.sh kanban show --column ready

# 2. Assign task to self
./activate.sh kanban assign TASK-005 agent

# 3. Move to in_progress
./activate.sh kanban move TASK-005 in_progress

# 4. View task details
./activate.sh kanban details TASK-005

# 5. Do the work...

# 6. Add completion note
./activate.sh kanban update TASK-005 --add-note "Implementation complete, tests passing"

# 7. Move to review
./activate.sh kanban move TASK-005 review

# 8. After review, move to done
./activate.sh kanban move TASK-005 done
```

### Human Developer Workflow

Same as above, but use `--assignee human` when assigning.

## Testing the Implementation

After implementation, test with:

```bash
# Initialize board
python kanban/kanban.py show

# Add test task
python kanban/kanban.py add \
  --title "Test task" \
  --description "Testing the kanban system" \
  --type feature \
  --priority medium \
  --assignee agent

# Move task through workflow
python kanban/kanban.py move TASK-001 ready
python kanban/kanban.py move TASK-001 in_progress
python kanban/kanban.py move TASK-001 review
python kanban/kanban.py move TASK-001 done

# Check stats
python kanban/kanban.py stats

# View completed task
python kanban/kanban.py details TASK-001
```

## Customization Options

You can customize:
- Column names and descriptions (in board-metadata.json)
- Task types and priority levels
- Required/optional fields in task template
- Color schemes in rich output
- Additional commands for your specific workflow

## Best Practices

1. **Version Control**: Commit board-metadata.json and all task files
2. **Task IDs**: Never reuse task IDs, even after deletion
3. **Descriptions**: Be specific and actionable
4. **Acceptance Criteria**: Define clear completion criteria
5. **Regular Updates**: Keep tasks current, add notes for blockers
6. **Clean Done**: Periodically archive completed tasks to `archive/` folder

## Benefits of This System

- ✅ **No merge conflicts** - Each task is independent
- ✅ **Git history** - Track task evolution over time
- ✅ **Parallel work** - Multiple people/agents work simultaneously
- ✅ **Scalable** - Performance doesn't degrade with task count
- ✅ **Visual** - Folder structure mirrors Kanban board
- ✅ **Simple** - Just file operations, no database needed
- ✅ **AI-friendly** - Perfect for autonomous agent workflows

## Example Project Structure After Implementation

```
project-root/
├── kanban/
│   ├── README.md
│   ├── board-metadata.json
│   ├── kanban.py
│   ├── backlog/
│   │   ├── TASK-001.json
│   │   └── TASK-002.json
│   ├── ready/
│   │   └── TASK-003.json
│   ├── in_progress/
│   │   └── TASK-004.json
│   ├── review/
│   │   └── TASK-005.json
│   └── done/
│       └── TASK-006.json
├── activate.sh
├── venv/
└── [rest of your project]
```

## Implementation Notes

- Make kanban.py executable: `chmod +x kanban/kanban.py`
- Create column folders: `mkdir -p kanban/{backlog,ready,in_progress,review,done}`
- Initialize metadata with next_task_number: 1
- Test all commands before considering complete
- Document any project-specific customizations in the README

## Support and Troubleshooting

Common issues:
- **"board-metadata.json not found"** - Initialize with template above
- **"Task not found"** - Use `list-files` command to locate
- **"Corrupted JSON"** - Validate with `python3 -m json.tool TASK-XXX.json`
- **Wrong task number** - Edit `next_task_number` in board-metadata.json

---

This system is designed for:
- AI/human collaborative development
- Clear task tracking and accountability
- Git-based workflow
- Self-service task management
- Scalability from small to large projects
