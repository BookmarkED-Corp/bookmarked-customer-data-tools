"""
ClassLink Snapshot Fetcher

Fetches all data from ClassLink API and creates daily snapshots.
Handles pagination, progress tracking, and error recovery.
"""
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog

from src.connectors.classlink import ClassLinkConnector
from src.snapshots.snapshot_manager import SnapshotManager
from src.snapshots.csv_writer import SnapshotWriter

logger = structlog.get_logger(__name__)


class ClassLinkSnapshotFetcher:
    """Fetches ClassLink data and creates snapshots"""

    def __init__(self, snapshot_manager: SnapshotManager):
        """
        Initialize ClassLinkSnapshotFetcher

        Args:
            snapshot_manager: SnapshotManager instance
        """
        self.snapshot_manager = snapshot_manager
        self.classlink = ClassLinkConnector()
        logger.info("ClassLinkSnapshotFetcher initialized")

    def fetch_all_users(self, bearer_token: str, oneroster_app_id: str,
                       limit: int = 2000, timeout: int = 60) -> List[Dict]:
        """
        Fetch ALL users from ClassLink (no role filter to avoid 1000 limit)

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            limit: Records per page (max 2000)
            timeout: Timeout per API call in seconds

        Returns:
            List of all users
        """
        all_users = []
        offset = 0
        page = 1
        api_call_count = 0

        logger.info("Starting ClassLink user fetch",
                   oneroster_app_id=oneroster_app_id,
                   limit=limit)

        while True:
            try:
                logger.info(f"Fetching users page {page}",
                           offset=offset,
                           limit=limit)

                start_time = time.time()

                # Fetch users with NO role filter (gets all)
                users = self.classlink.get_users(
                    bearer_token=bearer_token,
                    oneroster_app_id=oneroster_app_id,
                    limit=limit,
                    offset=offset,
                    role=None  # No filter - get ALL users
                )

                api_call_count += 1
                elapsed = time.time() - start_time

                logger.info(f"Page {page} fetched",
                           users_count=len(users),
                           elapsed_seconds=round(elapsed, 2),
                           total_users=len(all_users) + len(users))

                if not users or len(users) == 0:
                    logger.info("No more users to fetch")
                    break

                all_users.extend(users)

                # If we got less than limit, we're done
                if len(users) < limit:
                    logger.info("Last page fetched (partial page)")
                    break

                # Move to next page
                offset += limit
                page += 1

                # Small delay to be nice to API
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching users page {page}",
                            error=str(e),
                            offset=offset)
                # Don't fail entire fetch for one page error - continue
                break

        logger.info("All users fetched",
                   total_users=len(all_users),
                   api_calls=api_call_count,
                   pages=page)

        return all_users

    def fetch_entity_paginated(self, bearer_token: str, oneroster_app_id: str,
                               entity_type: str, limit: int = 2000) -> List[Dict]:
        """
        Fetch all records for an entity type (classes, schools, etc.)

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            entity_type: 'classes' or 'schools'
            limit: Records per page

        Returns:
            List of all records
        """
        all_records = []
        offset = 0
        page = 1

        logger.info(f"Starting {entity_type} fetch",
                   oneroster_app_id=oneroster_app_id)

        while True:
            try:
                logger.info(f"Fetching {entity_type} page {page}",
                           offset=offset,
                           limit=limit)

                start_time = time.time()

                if entity_type == 'classes':
                    records = self.classlink.get_classes(
                        bearer_token=bearer_token,
                        oneroster_app_id=oneroster_app_id,
                        limit=limit,
                        offset=offset
                    )
                elif entity_type == 'schools':
                    records = self.classlink.get_schools(
                        bearer_token=bearer_token,
                        oneroster_app_id=oneroster_app_id,
                        limit=limit,
                        offset=offset
                    )
                else:
                    logger.error(f"Unknown entity type: {entity_type}")
                    break

                elapsed = time.time() - start_time

                logger.info(f"{entity_type} page {page} fetched",
                           records_count=len(records),
                           elapsed_seconds=round(elapsed, 2))

                if not records or len(records) == 0:
                    break

                all_records.extend(records)

                if len(records) < limit:
                    break

                offset += limit
                page += 1
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching {entity_type} page {page}",
                            error=str(e))
                break

        logger.info(f"All {entity_type} fetched",
                   total_records=len(all_records),
                   pages=page)

        return all_records

    def create_snapshot(self, district_id: int, bearer_token: str, oneroster_app_id: str,
                       session_id: str, date: str = None) -> bool:
        """
        Create a complete ClassLink snapshot

        Args:
            district_id: District ID
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            session_id: Unique session identifier
            date: Snapshot date (YYYY-MM-DD), defaults to today

        Returns:
            True if successful, False otherwise
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        logger.info("Starting ClassLink snapshot creation",
                   district_id=district_id,
                   date=date,
                   session_id=session_id)

        # Initialize snapshot
        if not self.snapshot_manager.initialize_snapshot(district_id, date, 'classlink', session_id):
            logger.error("Failed to initialize snapshot")
            return False

        try:
            start_time = time.time()
            fetch_stats = {
                'total_api_calls': 0,
                'total_records': 0,
                'duration_seconds': 0,
                'errors': []
            }

            # Fetch all users (students, parents, teachers, etc.)
            logger.info("Fetching all users")
            all_users = self.fetch_all_users(bearer_token, oneroster_app_id)
            fetch_stats['total_api_calls'] += 1  # Simplified - actual count tracked in method

            # Separate by role
            students = [u for u in all_users if u.get('role') == 'student']
            parents = [u for u in all_users if u.get('role') in ['parent', 'guardian']]

            logger.info("Users categorized",
                       total_users=len(all_users),
                       students=len(students),
                       parents=len(parents))

            # Fetch classes
            logger.info("Fetching classes")
            classes = self.fetch_entity_paginated(bearer_token, oneroster_app_id, 'classes')
            fetch_stats['total_api_calls'] += 1

            # Fetch schools
            logger.info("Fetching schools")
            schools = self.fetch_entity_paginated(bearer_token, oneroster_app_id, 'schools')
            fetch_stats['total_api_calls'] += 1

            fetch_stats['total_records'] = len(all_users) + len(classes) + len(schools)

            # Write to CSV and JSONL
            snapshot_dir = self.snapshot_manager.get_snapshot_dir(district_id, date, 'classlink')
            writer = SnapshotWriter(snapshot_dir)

            files_metadata = {}

            # Write students
            if students:
                logger.info("Writing students data", count=len(students))
                files_metadata['students.csv'] = writer.write_entity_data('students', students)

            # Write parents
            if parents:
                logger.info("Writing parents data", count=len(parents))
                files_metadata['parents.csv'] = writer.write_entity_data('parents', parents)

            # Write classes
            if classes:
                logger.info("Writing classes data", count=len(classes))
                files_metadata['classes.csv'] = writer.write_entity_data('classes', classes)

            # Write schools
            if schools:
                logger.info("Writing schools data", count=len(schools))
                files_metadata['schools.csv'] = writer.write_entity_data('schools', schools)

            # Complete snapshot
            elapsed = time.time() - start_time
            fetch_stats['duration_seconds'] = int(elapsed)

            self.snapshot_manager.complete_snapshot(
                district_id=district_id,
                date=date,
                source_type='classlink',
                files=files_metadata,
                fetch_stats=fetch_stats
            )

            logger.info("ClassLink snapshot created successfully",
                       district_id=district_id,
                       date=date,
                       duration_seconds=fetch_stats['duration_seconds'],
                       total_records=fetch_stats['total_records'])

            return True

        except Exception as e:
            logger.error("ClassLink snapshot creation failed",
                        district_id=district_id,
                        error=str(e),
                        exc_info=True)

            # Mark snapshot as failed
            self.snapshot_manager.fail_snapshot(
                district_id=district_id,
                date=date,
                source_type='classlink',
                error=str(e)
            )

            # Clean up partial files
            self.snapshot_manager.cleanup_partial_snapshot(district_id, date, 'classlink')

            return False

    def create_snapshot_async(self, district_id: int, bearer_token: str, oneroster_app_id: str,
                             session_id: str, date: str = None):
        """
        Create snapshot in background thread

        Args:
            district_id: District ID
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            session_id: Unique session identifier
            date: Snapshot date (YYYY-MM-DD), defaults to today
        """
        import threading

        thread = threading.Thread(
            target=self.create_snapshot,
            args=(district_id, bearer_token, oneroster_app_id, session_id, date)
        )
        thread.daemon = True
        thread.start()

        logger.info("ClassLink snapshot creation started in background",
                   district_id=district_id,
                   session_id=session_id,
                   thread_id=thread.ident)
