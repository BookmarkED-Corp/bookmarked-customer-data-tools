# Customer Data Tools - Kanban Task Management

This directory contains all Kanban tasks for the Customer Data Tools project.

## 📁 Directory Structure

```
kanban/
├── backlog/          # All planned tasks (TASK-001 through TASK-040)
├── ready/            # Tasks ready to start
├── in_progress/      # Tasks currently being worked on
├── review/           # Tasks awaiting review
├── done/             # Completed tasks
├── kanban.py         # Python Kanban management tool
├── kanban_server.js  # Node.js Kanban UI server
├── README.md         # This file
├── TASK_SUMMARY.md   # Comprehensive task breakdown and statistics
└── PHASE_OVERVIEW.md # Visual phase overview and timeline
```

## 🚀 Quick Start

### View Kanban Board (Visual UI)

```bash
# From the project root directory
node kanban_server.js

# Then open in browser:
# http://localhost:3000
```

The visual Kanban board provides drag-and-drop task management with real-time updates.

### Using Python Kanban Tool

```bash
# List all tasks in backlog
python kanban/kanban.py list backlog

# Move task to in_progress
python kanban/kanban.py move TASK-001 in_progress

# Move task to done
python kanban/kanban.py move TASK-001 done

# Show task details
python kanban/kanban.py show TASK-001
```

## 📋 Task Format

Each task is a markdown file with YAML frontmatter:

```markdown
---
id: TASK-XXX
title: Task title here
type: feature|bug|docs|test|refactor
priority: critical|high|medium|low
assignee: agent|human|unassigned
phase: 1|2|3|4
estimated_hours: X
---

## Description
[Detailed description of the task]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Dependencies
- TASK-XXX (if any)

## Notes
[Any additional notes or context]
```

## 📊 Project Overview

**Total Tasks:** 40
**Total Estimated Hours:** 238 hours (~6 weeks)
**Phases:** 4

### Phase Breakdown

| Phase | Tasks | Hours | Focus |
|-------|-------|-------|-------|
| Phase 1 | 001-010 | 51h | Foundation (Flask, Auth, DB, Base Architecture) |
| Phase 2 | 011-020 | 67h | Core Tools (Student Mismatch, Missing Data, SIS Connectors) |
| Phase 3 | 021-030 | 62h | Advanced Features (HubSpot, Advanced Tools, Optimization) |
| Phase 4 | 031-040 | 58h | Deployment (AWS, Monitoring, Testing, Documentation) |

### Task Priorities

- **Critical (7 tasks):** Must be completed, blocks other work
- **High (26 tasks):** Important features and functionality
- **Medium (7 tasks):** Nice to have, enhances system

### Task Types

- **Feature (30):** New functionality
- **Test (4):** Testing and QA
- **Docs (2):** Documentation
- **Refactor (1):** Code optimization

## 🔄 Workflow

### Task Lifecycle

```
backlog → ready → in_progress → review → done
```

1. **backlog**: All planned tasks start here
2. **ready**: Tasks with dependencies met, ready to start
3. **in_progress**: Currently being worked on (limit 2-3 tasks)
4. **review**: Awaiting code review or testing
5. **done**: Completed and verified

### Moving Tasks

**Manual (File System):**
```bash
mv kanban/backlog/TASK-001.md kanban/in_progress/
```

**Using Python Tool:**
```bash
python kanban/kanban.py move TASK-001 in_progress
```

**Using Visual UI:**
Drag and drop tasks between columns

## 📖 Key Documents

### TASK_SUMMARY.md
Comprehensive breakdown of all 40 tasks including:
- Task statistics by type, priority, and phase
- Critical path dependencies
- Sprint recommendations
- Parallel work opportunities
- Success metrics

### PHASE_OVERVIEW.md
Visual overview including:
- Phase-by-phase task lists
- Timeline and milestones
- Dependency flow diagrams
- Deliverables by phase
- Success criteria

## 🎯 Getting Started

### For Developers Starting Phase 1

1. Review `PHASE_OVERVIEW.md` for context
2. Read `TASK-001.md` in backlog
3. Move TASK-001 to `in_progress`
4. Complete acceptance criteria
5. Move to `review` when done
6. After review approval, move to `done`
7. Start TASK-002

### For Project Managers

1. Review `TASK_SUMMARY.md` for overall scope
2. Use visual Kanban board for tracking
3. Monitor tasks in `in_progress` (should be 2-3 max)
4. Check `PHASE_OVERVIEW.md` for milestone tracking
5. Update sprint plans based on completed tasks

## 🔍 Task Dependencies

Tasks have dependencies listed in their frontmatter and "Dependencies" section. Before starting a task:

1. Check the Dependencies section
2. Verify all dependent tasks are in `done`
3. If dependencies not met, leave in `backlog` or `ready`

**Example Critical Path:**
```
TASK-001 → TASK-002 → TASK-023 → TASK-024 → TASK-026
(Flask)    (Auth)     (HubSpot)  (Tickets)   (UI)
```

## 📈 Progress Tracking

### Manual Tracking

Count tasks in each column:
```bash
ls kanban/backlog/ | wc -l      # Tasks not started
ls kanban/in_progress/ | wc -l  # Tasks in progress
ls kanban/done/ | wc -l         # Tasks completed
```

### Visual Tracking

Use the Kanban UI server for real-time visual progress tracking.

### Progress Formula

```
Progress % = (Tasks in done / Total tasks) × 100
```

## 🏷️ Task Naming Convention

Tasks are numbered sequentially:
- `TASK-001` to `TASK-010`: Phase 1
- `TASK-011` to `TASK-020`: Phase 2
- `TASK-021` to `TASK-030`: Phase 3
- `TASK-031` to `TASK-040`: Phase 4

File naming: `TASK-XXX.md` (e.g., `TASK-001.md`)

## 🤝 Contributing

### Adding New Tasks

1. Create new markdown file in `kanban/backlog/`
2. Use next available TASK number
3. Follow task format template
4. Include all required frontmatter fields
5. Add to appropriate phase
6. Update dependencies in related tasks

### Updating Existing Tasks

1. Edit the task markdown file
2. Update acceptance criteria as needed
3. Add notes for important findings
4. Update estimated hours if needed
5. Keep Dependencies section current

### Completing Tasks

1. Check all acceptance criteria boxes
2. Move task to `review`
3. After approval, move to `done`
4. Update dependent tasks if needed

## 🛠️ Tools

### Kanban Server (Recommended)

**Features:**
- Visual drag-and-drop interface
- Real-time updates
- Task filtering and search
- Progress visualization
- Mobile-friendly

**Start server:**
```bash
node kanban_server.js
```

### Python Kanban Tool

**Features:**
- Command-line task management
- Quick task movement
- Task listing and filtering
- Task details display

**Common commands:**
```bash
# List tasks
python kanban/kanban.py list backlog
python kanban/kanban.py list in_progress

# Move task
python kanban/kanban.py move TASK-001 ready

# Show task
python kanban/kanban.py show TASK-001

# Search tasks
python kanban/kanban.py search "database"
```

## 📚 Related Documentation

- **PROJECT_REQUIREMENTS.md**: Complete project requirements
- **docs/ARCHITECTURE.md**: System architecture details
- **CLAUDE.md**: Claude Code guidance
- **README.md**: Project overview

## ❓ FAQ

**Q: How do I know which task to start next?**
A: Check `PHASE_OVERVIEW.md` for the recommended order. Start with Phase 1, Task 001, and work sequentially unless dependencies allow parallel work.

**Q: Can I work on multiple tasks at once?**
A: Yes, but limit work-in-progress to 2-3 tasks maximum to maintain focus and momentum.

**Q: What if I find a task's estimate is wrong?**
A: Update the `estimated_hours` in the task's frontmatter and document the reason in Notes.

**Q: How do I handle blocked tasks?**
A: Add a note explaining the blocker, update dependencies if needed, and move to a different task if possible.

**Q: Should I create new tasks for bugs found during development?**
A: Minor bugs should be handled as part of the current task. Major bugs or new features should get new task files.

**Q: What do I do when all Phase 1 tasks are done?**
A: Celebrate! Then review Phase 2 tasks and begin with TASK-011.

## 🎉 Success Metrics

Track these metrics throughout development:

- **Velocity**: Tasks completed per week
- **Accuracy**: Estimated hours vs actual hours
- **Quality**: Tasks requiring rework
- **Blockers**: Tasks stuck > 3 days

## 📞 Support

For questions about tasks or the Kanban system:
1. Review task notes and acceptance criteria
2. Check TASK_SUMMARY.md for context
3. Consult PROJECT_REQUIREMENTS.md for requirements
4. Ask team members or project lead

---

**Last Updated:** 2025-10-14
**Total Tasks:** 40
**Status:** All tasks in backlog, ready to begin
