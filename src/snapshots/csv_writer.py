"""
CSV and JSONL Writer

Handles writing snapshot data to CSV (filtered columns) and JSONL (full payloads) formats.
Streams data to avoid loading large datasets into memory.
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import structlog

logger = structlog.get_logger(__name__)


class SnapshotWriter:
    """Writes snapshot data to CSV and JSONL formats"""

    # Column definitions for each entity type
    COLUMNS = {
        'students': ['sourcedId', 'givenName', 'familyName', 'email', 'grade', 'status', 'identifier'],
        'parents': ['sourcedId', 'givenName', 'familyName', 'email', 'phone', 'sms', 'role', 'status'],
        'classes': ['sourcedId', 'title', 'classCode', 'classType', 'subjects', 'status'],
        'schools': ['sourcedId', 'name', 'type', 'identifier', 'status'],
        'enrollments': ['sourcedId', 'userId', 'classSourcedId', 'schoolSourcedId', 'role', 'status', 'beginDate', 'endDate']
    }

    def __init__(self, snapshot_dir: Path):
        """
        Initialize SnapshotWriter

        Args:
            snapshot_dir: Directory to write snapshot files
        """
        self.snapshot_dir = snapshot_dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        logger.info("SnapshotWriter initialized", snapshot_dir=str(snapshot_dir))

    def write_entity_data(self, entity_type: str, data: List[Dict[str, Any]],
                         progress_callback: Callable[[int], None] = None) -> Dict[str, Any]:
        """
        Write entity data to both CSV and JSONL files

        Args:
            entity_type: Type of entity ('students', 'parents', 'classes', etc.)
            data: List of entity dictionaries
            progress_callback: Optional callback function(current_row) for progress tracking

        Returns:
            Dict with file metadata (rows, size_bytes, columns)
        """
        if entity_type not in self.COLUMNS:
            raise ValueError(f"Unknown entity type: {entity_type}")

        csv_path = self.snapshot_dir / f'{entity_type}.csv'
        jsonl_path = self.snapshot_dir / f'{entity_type}.jsonl'
        columns = self.COLUMNS[entity_type]

        logger.info(f"Writing {entity_type} data",
                   record_count=len(data),
                   csv_path=str(csv_path),
                   jsonl_path=str(jsonl_path))

        rows_written = 0

        # Write CSV and JSONL simultaneously
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file, \
             open(jsonl_path, 'w', encoding='utf-8') as jsonl_file:

            csv_writer = csv.DictWriter(csv_file, fieldnames=columns, extrasaction='ignore')
            csv_writer.writeheader()

            for idx, record in enumerate(data):
                # Write to CSV (filtered columns)
                csv_writer.writerow(record)

                # Write to JSONL (full payload)
                jsonl_file.write(json.dumps(record) + '\n')

                rows_written += 1

                # Progress callback
                if progress_callback and idx % 100 == 0:
                    progress_callback(idx + 1)

        # Get file sizes
        csv_size = csv_path.stat().st_size
        jsonl_size = jsonl_path.stat().st_size

        metadata = {
            'rows': rows_written,
            'size_bytes': csv_size,
            'columns': columns,
            'jsonl_size_bytes': jsonl_size
        }

        logger.info(f"{entity_type} data written successfully",
                   rows=rows_written,
                   csv_size_mb=round(csv_size / 1024 / 1024, 2),
                   jsonl_size_mb=round(jsonl_size / 1024 / 1024, 2))

        return metadata

    def search_csv(self, entity_type: str, search_query: str,
                   search_columns: List[str] = None, limit: int = 50) -> List[Dict[str, str]]:
        """
        Search CSV file without loading entire file into memory

        Args:
            entity_type: Type of entity ('students', 'parents', etc.)
            search_query: Search term
            search_columns: Columns to search (default: all text columns)
            limit: Maximum results to return

        Returns:
            List of matching records
        """
        csv_path = self.snapshot_dir / f'{entity_type}.csv'

        if not csv_path.exists():
            logger.warning(f"{entity_type} CSV not found", path=str(csv_path))
            return []

        # Default search columns
        if search_columns is None:
            if entity_type == 'students':
                search_columns = ['givenName', 'familyName', 'email', 'sourcedId', 'identifier']
            elif entity_type == 'parents':
                search_columns = ['givenName', 'familyName', 'email', 'phone', 'sourcedId']
            elif entity_type == 'classes':
                search_columns = ['title', 'classCode', 'sourcedId']
            else:
                search_columns = []

        results = []
        query_lower = search_query.lower()

        logger.info(f"Searching {entity_type} CSV",
                   query=search_query,
                   search_columns=search_columns,
                   limit=limit)

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Search across specified columns
                    if any(query_lower in str(row.get(col, '')).lower() for col in search_columns):
                        results.append(row)

                        if len(results) >= limit:
                            break

            logger.info(f"Search completed",
                       entity_type=entity_type,
                       results_count=len(results))

        except Exception as e:
            logger.error(f"Error searching {entity_type} CSV",
                        error=str(e),
                        path=str(csv_path))
            return []

        return results

    def get_record_by_sourced_id(self, entity_type: str, sourced_id: str) -> Optional[Dict[str, str]]:
        """
        Get a single record by sourcedId

        Args:
            entity_type: Type of entity
            sourced_id: SourcedId to find

        Returns:
            Record dict or None
        """
        results = self.search_csv(entity_type, sourced_id, search_columns=['sourcedId'], limit=1)
        return results[0] if results else None

    def get_full_payload(self, entity_type: str, sourced_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full JSON payload for a record from JSONL file

        Args:
            entity_type: Type of entity
            sourced_id: SourcedId to find

        Returns:
            Full record dict or None
        """
        jsonl_path = self.snapshot_dir / f'{entity_type}.jsonl'

        if not jsonl_path.exists():
            logger.warning(f"{entity_type} JSONL not found", path=str(jsonl_path))
            return None

        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line)
                    if record.get('sourcedId') == sourced_id:
                        logger.info("Full payload found",
                                   entity_type=entity_type,
                                   sourced_id=sourced_id)
                        return record

            logger.debug("Record not found in JSONL",
                        entity_type=entity_type,
                        sourced_id=sourced_id)
            return None

        except Exception as e:
            logger.error(f"Error reading {entity_type} JSONL",
                        error=str(e),
                        path=str(jsonl_path))
            return None

    def get_file_stats(self, entity_type: str) -> Dict[str, Any]:
        """
        Get statistics about a snapshot file

        Args:
            entity_type: Type of entity

        Returns:
            Dict with stats (rows, size_bytes, exists)
        """
        csv_path = self.snapshot_dir / f'{entity_type}.csv'
        jsonl_path = self.snapshot_dir / f'{entity_type}.jsonl'

        stats = {
            'entity_type': entity_type,
            'csv_exists': csv_path.exists(),
            'jsonl_exists': jsonl_path.exists(),
            'rows': 0,
            'csv_size_bytes': 0,
            'jsonl_size_bytes': 0
        }

        if csv_path.exists():
            stats['csv_size_bytes'] = csv_path.stat().st_size

            # Count rows
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    stats['rows'] = sum(1 for _ in reader)
            except Exception as e:
                logger.error("Error counting CSV rows", error=str(e))

        if jsonl_path.exists():
            stats['jsonl_size_bytes'] = jsonl_path.stat().st_size

        return stats
