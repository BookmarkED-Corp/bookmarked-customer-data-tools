---
id: TASK-006
title: Create base diagnostic tool class and architecture
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 6
---

## Description
Implement the abstract `BaseTool` class that all diagnostic tools will extend. Define the plugin architecture, common interfaces, and shared functionality for data gathering and comparison.

## Acceptance Criteria
- [ ] `BaseTool` abstract class created in `src/tools/base_tool.py`
- [ ] Abstract methods defined: `get_inputs()`, `run()`, `get_status()`, `get_remediation()`
- [ ] Customer configuration loading in `__init__()`
- [ ] Source connector initialization method
- [ ] Bookmarked connector initialization method
- [ ] Common data comparison utilities
- [ ] Error handling framework
- [ ] Logging standardized across all tools
- [ ] DiagnosticResult model created in `src/models/diagnostic_result.py`
- [ ] Status constants defined: ISSUE_IN_SOURCE, ISSUE_IN_BOOKMARKED, NO_ISSUE, BOTH_SOURCES_HAVE_ISSUE

## Dependencies
- TASK-005

## Notes
- Design for extensibility - new tools should be easy to add
- Include helper methods for common comparison patterns
- Standardize error reporting
- Support timeout handling for long-running tools
