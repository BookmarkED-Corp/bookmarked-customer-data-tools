---
id: TASK-025
title: Create tool recommendation engine
type: feature
priority: medium
assignee: agent
phase: 3
estimated_hours: 6
---

## Description
Implement intelligent tool recommendation system that analyzes HubSpot ticket descriptions and suggests the most appropriate diagnostic tool. Include confidence scoring and multiple tool suggestions.

## Acceptance Criteria
- [ ] Tool selector class created
- [ ] Keyword-based matching for tool selection
- [ ] Issue type classification logic
- [ ] Confidence scoring for recommendations
- [ ] Support for multiple tool suggestions (ranked)
- [ ] Default to manual selection if confidence low
- [ ] Learning from past tool selections (optional)
- [ ] UI displaying recommended tools with confidence
- [ ] Ability to override recommendation
- [ ] Unit tests for classification logic

## Dependencies
- TASK-024

## Notes
- Start with simple keyword matching
- Consider ML-based classification in future
- Include common issue patterns
- Allow manual tool selection always
