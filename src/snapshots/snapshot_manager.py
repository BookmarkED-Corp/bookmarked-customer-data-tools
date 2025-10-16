"""
Snapshot Manager

Manages daily snapshots of ClassLink and OneRoster data for fast offline searching.
Handles snapshot creation, status tracking, locking, and cleanup.
"""
import os
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import time
import structlog

logger = structlog.get_logger(__name__)


class SnapshotManager:
    """Manages daily snapshots of integration data"""

    def __init__(self, base_path: str = 'snapshots'):
        """
        Initialize SnapshotManager

        Args:
            base_path: Root directory for all snapshots
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info("SnapshotManager initialized", base_path=str(self.base_path))

    def get_snapshot_dir(self, district_id: int, date: str, source_type: str) -> Path:
        """
        Get snapshot directory path

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'

        Returns:
            Path to snapshot directory
        """
        return self.base_path / str(district_id) / date / source_type

    def get_status_path(self, district_id: int, date: str, source_type: str) -> Path:
        """Get path to status.json file"""
        return self.get_snapshot_dir(district_id, date, source_type) / 'status.json'

    def get_lock_path(self, district_id: int, date: str, source_type: str) -> Path:
        """Get path to .lock file"""
        return self.get_snapshot_dir(district_id, date, source_type) / '.lock'

    def get_snapshot(self, district_id: int, date: str, source_type: str) -> Optional[Dict[str, Any]]:
        """
        Get snapshot metadata

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'

        Returns:
            Snapshot metadata dict or None if not exists
        """
        status_path = self.get_status_path(district_id, date, source_type)

        if not status_path.exists():
            logger.debug("Snapshot not found",
                        district_id=district_id,
                        date=date,
                        source_type=source_type)
            return None

        try:
            with open(status_path, 'r') as f:
                status = json.load(f)

            logger.info("Snapshot found",
                       district_id=district_id,
                       date=date,
                       source_type=source_type,
                       status=status.get('status'))
            return status
        except Exception as e:
            logger.error("Error reading snapshot status",
                        error=str(e),
                        status_path=str(status_path))
            return None

    def get_latest_snapshot(self, district_id: int, source_type: str) -> Optional[Dict[str, Any]]:
        """
        Get most recent snapshot for a district and source type

        Args:
            district_id: District ID
            source_type: 'classlink' or 'oneroster'

        Returns:
            Snapshot metadata dict or None
        """
        district_dir = self.base_path / str(district_id)

        if not district_dir.exists():
            logger.debug("No snapshots found for district", district_id=district_id)
            return None

        # Get all date directories
        date_dirs = [d for d in district_dir.iterdir() if d.is_dir()]
        date_dirs.sort(reverse=True)  # Most recent first

        for date_dir in date_dirs:
            snapshot = self.get_snapshot(district_id, date_dir.name, source_type)
            if snapshot and snapshot.get('status') == 'complete':
                logger.info("Latest snapshot found",
                           district_id=district_id,
                           date=date_dir.name,
                           source_type=source_type)
                return snapshot

        logger.debug("No complete snapshots found",
                    district_id=district_id,
                    source_type=source_type)
        return None

    def is_snapshot_in_progress(self, district_id: int, date: str, source_type: str) -> bool:
        """
        Check if a snapshot fetch is currently in progress

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'

        Returns:
            True if in progress, False otherwise
        """
        # Check lock file
        lock_path = self.get_lock_path(district_id, date, source_type)
        if lock_path.exists():
            try:
                with open(lock_path, 'r') as f:
                    lock_data = json.load(f)

                # Check if lock is stale (> 30 minutes old)
                started_at = datetime.fromisoformat(lock_data.get('started_at', ''))
                age_minutes = (datetime.now() - started_at).total_seconds() / 60

                if age_minutes > 30:
                    logger.warning("Stale lock detected",
                                  district_id=district_id,
                                  date=date,
                                  source_type=source_type,
                                  age_minutes=age_minutes)
                    # Remove stale lock
                    lock_path.unlink()
                    return False

                logger.info("Snapshot fetch in progress",
                           district_id=district_id,
                           date=date,
                           source_type=source_type,
                           age_minutes=age_minutes,
                           session_id=lock_data.get('session_id'))
                return True
            except Exception as e:
                logger.error("Error checking lock file", error=str(e))
                return False

        # Check status.json
        status = self.get_snapshot(district_id, date, source_type)
        if status and status.get('status') == 'fetching':
            # Double-check it's not stale
            started_at = datetime.fromisoformat(status.get('started_at', ''))
            age_minutes = (datetime.now() - started_at).total_seconds() / 60

            if age_minutes > 30:
                logger.warning("Stale snapshot status detected",
                              district_id=district_id,
                              date=date,
                              source_type=source_type,
                              age_minutes=age_minutes)
                return False

            return True

        return False

    def create_lock(self, district_id: int, date: str, source_type: str, session_id: str) -> bool:
        """
        Create lock file for snapshot creation

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            session_id: Unique session identifier

        Returns:
            True if lock created successfully, False if already locked
        """
        lock_path = self.get_lock_path(district_id, date, source_type)

        # Check if already locked
        if lock_path.exists():
            logger.warning("Lock already exists",
                          district_id=district_id,
                          date=date,
                          source_type=source_type)
            return False

        # Create directory if needed
        lock_path.parent.mkdir(parents=True, exist_ok=True)

        # Create lock file (atomic operation with 'x' mode)
        try:
            with open(lock_path, 'x') as f:
                json.dump({
                    'session_id': session_id,
                    'started_at': datetime.now().isoformat(),
                    'pid': os.getpid()
                }, f)

            logger.info("Lock created",
                       district_id=district_id,
                       date=date,
                       source_type=source_type,
                       session_id=session_id)
            return True
        except FileExistsError:
            logger.warning("Lock creation race condition",
                          district_id=district_id,
                          date=date,
                          source_type=source_type)
            return False

    def release_lock(self, district_id: int, date: str, source_type: str):
        """
        Release lock file

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
        """
        lock_path = self.get_lock_path(district_id, date, source_type)

        if lock_path.exists():
            lock_path.unlink()
            logger.info("Lock released",
                       district_id=district_id,
                       date=date,
                       source_type=source_type)

    def initialize_snapshot(self, district_id: int, date: str, source_type: str, session_id: str) -> bool:
        """
        Initialize a new snapshot with status='fetching'

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            session_id: Unique session identifier

        Returns:
            True if initialized successfully, False if already in progress
        """
        # Check if already in progress
        if self.is_snapshot_in_progress(district_id, date, source_type):
            logger.warning("Snapshot already in progress",
                          district_id=district_id,
                          date=date,
                          source_type=source_type)
            return False

        # Create lock
        if not self.create_lock(district_id, date, source_type, session_id):
            return False

        # Create initial status.json
        snapshot_dir = self.get_snapshot_dir(district_id, date, source_type)
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        status = {
            'district_id': district_id,
            'snapshot_date': date,
            'source_type': source_type,
            'status': 'fetching',
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'fetched_by_session': session_id,
            'files': {},
            'fetch_stats': {
                'total_api_calls': 0,
                'total_records': 0,
                'duration_seconds': 0,
                'errors': []
            }
        }

        self.update_status(district_id, date, source_type, status)

        logger.info("Snapshot initialized",
                   district_id=district_id,
                   date=date,
                   source_type=source_type,
                   session_id=session_id)
        return True

    def update_status(self, district_id: int, date: str, source_type: str, status: Dict[str, Any]):
        """
        Update snapshot status.json

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            status: Status dict to write
        """
        status_path = self.get_status_path(district_id, date, source_type)
        status_path.parent.mkdir(parents=True, exist_ok=True)

        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2)

        logger.debug("Status updated",
                    district_id=district_id,
                    date=date,
                    source_type=source_type,
                    status=status.get('status'))

    def complete_snapshot(self, district_id: int, date: str, source_type: str,
                         files: Dict[str, Dict], fetch_stats: Dict[str, Any]):
        """
        Mark snapshot as complete

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            files: File metadata dict
            fetch_stats: Fetch statistics dict
        """
        status = self.get_snapshot(district_id, date, source_type)
        if not status:
            logger.error("Cannot complete snapshot - status not found")
            return

        status['status'] = 'complete'
        status['completed_at'] = datetime.now().isoformat()
        status['files'] = files
        status['fetch_stats'] = fetch_stats

        # Calculate duration
        started_at = datetime.fromisoformat(status['started_at'])
        completed_at = datetime.fromisoformat(status['completed_at'])
        status['fetch_stats']['duration_seconds'] = int((completed_at - started_at).total_seconds())

        self.update_status(district_id, date, source_type, status)
        self.release_lock(district_id, date, source_type)

        logger.info("Snapshot completed",
                   district_id=district_id,
                   date=date,
                   source_type=source_type,
                   duration_seconds=status['fetch_stats']['duration_seconds'])

    def fail_snapshot(self, district_id: int, date: str, source_type: str, error: str):
        """
        Mark snapshot as failed

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            error: Error message
        """
        status = self.get_snapshot(district_id, date, source_type)
        if not status:
            logger.error("Cannot fail snapshot - status not found")
            return

        status['status'] = 'failed'
        status['completed_at'] = datetime.now().isoformat()
        status['fetch_stats']['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': error
        })

        self.update_status(district_id, date, source_type, status)
        self.release_lock(district_id, date, source_type)

        logger.error("Snapshot failed",
                    district_id=district_id,
                    date=date,
                    source_type=source_type,
                    error=error)

    def cleanup_partial_snapshot(self, district_id: int, date: str, source_type: str):
        """
        Remove partial snapshot files on failure

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
        """
        snapshot_dir = self.get_snapshot_dir(district_id, date, source_type)

        if snapshot_dir.exists():
            # Remove all files except status.json
            for file in snapshot_dir.iterdir():
                if file.name != 'status.json' and file.name != '.lock':
                    file.unlink()
                    logger.debug("Deleted partial file", file=str(file))

            logger.info("Partial snapshot cleaned up",
                       district_id=district_id,
                       date=date,
                       source_type=source_type)

    def cleanup_old_snapshots(self, district_id: int, retention_days: int = 30):
        """
        Remove snapshots older than retention period

        Args:
            district_id: District ID
            retention_days: Number of days to retain snapshots
        """
        district_dir = self.base_path / str(district_id)

        if not district_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        removed_count = 0

        for date_dir in district_dir.iterdir():
            if not date_dir.is_dir():
                continue

            try:
                snapshot_date = datetime.strptime(date_dir.name, '%Y-%m-%d')
                if snapshot_date < cutoff_date:
                    # Remove entire date directory
                    for file in date_dir.rglob('*'):
                        if file.is_file():
                            file.unlink()
                    for subdir in reversed(list(date_dir.rglob('*'))):
                        if subdir.is_dir():
                            subdir.rmdir()
                    date_dir.rmdir()
                    removed_count += 1
                    logger.info("Removed old snapshot",
                               district_id=district_id,
                               date=date_dir.name)
            except ValueError:
                logger.warning("Invalid date directory name", dir_name=date_dir.name)

        logger.info("Old snapshots cleaned up",
                   district_id=district_id,
                   removed_count=removed_count,
                   retention_days=retention_days)

    def search_snapshot(self, district_id: int, date: str, source_type: str,
                       entity_type: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search snapshot CSV files for matching records

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            entity_type: 'students', 'parents', 'teachers', 'classes', 'schools'
            search_term: Search term (case-insensitive, partial match)

        Returns:
            List of matching records as dicts
        """
        snapshot_dir = self.get_snapshot_dir(district_id, date, source_type)
        csv_path = snapshot_dir / f'{entity_type}.csv'

        if not csv_path.exists():
            logger.warning("Snapshot CSV not found",
                          district_id=district_id,
                          date=date,
                          source_type=source_type,
                          entity_type=entity_type,
                          csv_path=str(csv_path))
            return []

        matches = []
        search_lower = search_term.lower()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Search across all fields
                    found = False
                    for key, value in row.items():
                        if value and search_lower in str(value).lower():
                            found = True
                            break

                    if found:
                        matches.append(row)

            logger.info("Snapshot search completed",
                       district_id=district_id,
                       date=date,
                       entity_type=entity_type,
                       search_term=search_term,
                       matches_found=len(matches))

            return matches

        except Exception as e:
            logger.error("Error searching snapshot",
                        district_id=district_id,
                        date=date,
                        entity_type=entity_type,
                        error=str(e))
            return []

    def get_parent_children_from_jsonl(self, district_id: int, date: str, source_type: str,
                                       parent_sourced_id: str) -> List[Dict[str, Any]]:
        """
        Get children for a parent by reading agents array from JSONL

        Args:
            district_id: District ID
            date: Date string (YYYY-MM-DD)
            source_type: 'classlink' or 'oneroster'
            parent_sourced_id: Parent's sourcedId

        Returns:
            List of child student records
        """
        snapshot_dir = self.get_snapshot_dir(district_id, date, source_type)
        parents_jsonl = snapshot_dir / 'parents.jsonl'
        students_jsonl = snapshot_dir / 'students.jsonl'

        if not parents_jsonl.exists() or not students_jsonl.exists():
            logger.warning("JSONL files not found for parent-child lookup",
                          district_id=district_id,
                          date=date)
            return []

        try:
            # Find the parent record and get agents
            parent_record = None
            with open(parents_jsonl, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line)
                    if record.get('sourcedId') == parent_sourced_id:
                        parent_record = record
                        break

            if not parent_record:
                logger.warning("Parent not found in JSONL",
                              parent_sourced_id=parent_sourced_id)
                return []

            # Get student sourcedIds from agents array
            agents = parent_record.get('agents', [])
            logger.info("Found agents array",
                       parent_sourced_id=parent_sourced_id,
                       agents_count=len(agents),
                       agents=agents)

            student_sourced_ids = [agent.get('sourcedId') for agent in agents
                                  if agent.get('type') == 'user']

            logger.info("Extracted student sourcedIds from agents",
                       parent_sourced_id=parent_sourced_id,
                       student_sourced_ids=student_sourced_ids)

            if not student_sourced_ids:
                logger.info("No children found in parent agents array",
                           parent_sourced_id=parent_sourced_id)
                return []

            # Find matching students
            children = []
            with open(students_jsonl, 'r', encoding='utf-8') as f:
                for line in f:
                    student = json.loads(line)
                    if student.get('sourcedId') in student_sourced_ids:
                        children.append({
                            'sourcedId': student.get('sourcedId'),
                            'givenName': student.get('givenName'),
                            'familyName': student.get('familyName'),
                            'email': student.get('email'),
                            'grade': student.get('grades', [''])[0] if student.get('grades') else None,
                            'identifier': student.get('identifier')
                        })

            logger.info("Children retrieved from JSONL",
                       parent_sourced_id=parent_sourced_id,
                       children_count=len(children))

            return children

        except Exception as e:
            logger.error("Error getting parent children from JSONL",
                        district_id=district_id,
                        parent_sourced_id=parent_sourced_id,
                        error=str(e))
            return []
