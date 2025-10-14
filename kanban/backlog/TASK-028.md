---
id: TASK-028
title: Create FTP connector for customer data files
type: feature
priority: medium
assignee: agent
phase: 3
estimated_hours: 6
---

## Description
Implement FTP client for accessing customer-hosted data files. Support per-customer FTP configurations with secure credential handling and file caching.

## Acceptance Criteria
- [ ] `FTPClient` class created in `src/connectors/ftp_client.py`
- [ ] Per-customer FTP configuration support
- [ ] Secure credential handling from environment/Secrets Manager
- [ ] File download functionality
- [ ] File caching to avoid repeated downloads
- [ ] Support for common file formats (CSV, ZIP, XLSX)
- [ ] Error handling for connection failures
- [ ] Timeout configuration (30 seconds)
- [ ] List directory contents
- [ ] Integration tests with mock FTP server

## Dependencies
- TASK-005
- TASK-008

## Notes
- Use ftplib or pysftp library
- Support both FTP and SFTP
- Implement connection pooling
- Clean up cached files after processing
