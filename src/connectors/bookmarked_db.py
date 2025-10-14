"""
Bookmarked Database Connector

Read-only PostgreSQL connector for Bookmarked staging and production databases.
"""
import os
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import structlog

logger = structlog.get_logger(__name__)


class BookmarkedDBConnector:
    """Read-only connector for Bookmarked PostgreSQL databases"""

    def __init__(self, environment: str = 'staging'):
        """
        Initialize database connector

        Args:
            environment: 'staging' or 'production'
        """
        self.environment = environment
        self.engine = None
        self._connection_params = None

    def test_connection(self, host: str, port: int, database: str,
                       user: str, password: str) -> Dict[str, Any]:
        """
        Test database connection with provided credentials

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database username
            password: Database password

        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            # Build connection URL
            connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

            # Create test engine with minimal pool
            test_engine = create_engine(
                connection_url,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True,
                connect_args={
                    'connect_timeout': 10,
                    'options': '-c default_transaction_read_only=on'
                }
            )

            # Test connection
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()

                # Get database version
                version_result = conn.execute(text("SELECT version()"))
                version = version_result.fetchone()[0]

            test_engine.dispose()

            logger.info("Database connection test successful",
                       environment=self.environment,
                       host=host,
                       database=database)

            return {
                'success': True,
                'message': 'Connection successful',
                'details': {
                    'host': host,
                    'port': port,
                    'database': database,
                    'version': version[:50]  # Truncate version string
                }
            }

        except SQLAlchemyError as e:
            logger.error("Database connection test failed",
                        environment=self.environment,
                        error=str(e))
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'details': None
            }
        except Exception as e:
            logger.error("Unexpected error testing database connection",
                        environment=self.environment,
                        error=str(e))
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'details': None
            }

    def connect(self, host: str, port: int, database: str,
                user: str, password: str) -> bool:
        """
        Establish database connection

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database username
            password: Database password

        Returns:
            True if connection successful
        """
        try:
            connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

            self.engine = create_engine(
                connection_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    'connect_timeout': 30,
                    'options': '-c default_transaction_read_only=on'
                }
            )

            # Store connection params for later use
            self._connection_params = {
                'host': host,
                'port': port,
                'database': database,
                'user': user
            }

            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Database connection established",
                       environment=self.environment,
                       host=host,
                       database=database)

            return True

        except Exception as e:
            logger.error("Failed to establish database connection",
                        environment=self.environment,
                        error=str(e))
            return False

    def disconnect(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            logger.info("Database connection closed", environment=self.environment)

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a read-only query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                return rows

        except Exception as e:
            logger.error("Query execution failed",
                        environment=self.environment,
                        error=str(e),
                        query=query[:100])
            raise

    def get_students(self, organization_id: Optional[int] = None,
                    limit: int = 100) -> List[Dict]:
        """
        Get students from database

        Args:
            organization_id: Filter by organization ID
            limit: Maximum number of results

        Returns:
            List of student records
        """
        query = """
            SELECT id, external_id, first_name, last_name, email,
                   organization_id, created_at, updated_at
            FROM students
        """

        params = {}
        if organization_id:
            query += " WHERE organization_id = :org_id"
            params['org_id'] = organization_id

        query += " LIMIT :limit"
        params['limit'] = limit

        return self.execute_query(query, params)

    def get_organizations(self, limit: int = 100) -> List[Dict]:
        """
        Get organizations from database

        Args:
            limit: Maximum number of results

        Returns:
            List of organization records
        """
        query = """
            SELECT id, name, external_id, type,
                   created_at, updated_at
            FROM organizations
            LIMIT :limit
        """

        return self.execute_query(query, {'limit': limit})
