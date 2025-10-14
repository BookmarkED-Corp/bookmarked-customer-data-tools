"""
Tests for ClickUp API Connector

Tests the ClickUp connector functionality including connection testing,
team/space/list/task operations.
"""
import pytest
from src.connectors.clickup import ClickUpConnector
import os


@pytest.fixture
def clickup_connector():
    """Fixture to create ClickUp connector instance"""
    return ClickUpConnector()


@pytest.fixture
def api_key():
    """Fixture to get API key from environment"""
    key = os.getenv('CLICKUP_API_KEY')
    if not key:
        pytest.skip("CLICKUP_API_KEY not set in environment")
    return key


class TestClickUpConnection:
    """Test ClickUp connection functionality"""

    def test_connector_initialization(self, clickup_connector):
        """Test that connector initializes properly"""
        assert clickup_connector is not None
        assert clickup_connector.api_url == 'https://api.clickup.com/api/v2'

    def test_test_connection_success(self, clickup_connector, api_key):
        """Test successful connection to ClickUp API"""
        result = clickup_connector.test_connection(api_key)

        assert result['success'] is True
        assert 'Connected to ClickUp successfully' in result['message']
        assert result['details'] is not None
        assert 'user_id' in result['details']
        assert 'username' in result['details']

    def test_test_connection_invalid_key(self, clickup_connector):
        """Test connection with invalid API key"""
        result = clickup_connector.test_connection('invalid_key')

        assert result['success'] is False
        assert 'Connection failed' in result['message']

    def test_test_connection_empty_key(self, clickup_connector):
        """Test connection with empty API key"""
        result = clickup_connector.test_connection('')

        assert result['success'] is False


class TestClickUpTeams:
    """Test ClickUp teams (workspaces) functionality"""

    def test_get_teams(self, clickup_connector, api_key):
        """Test getting teams/workspaces"""
        teams = clickup_connector.get_teams(api_key)

        assert isinstance(teams, list)
        # Should have at least one team
        if len(teams) > 0:
            team = teams[0]
            assert 'id' in team
            assert 'name' in team

    def test_get_teams_invalid_key(self, clickup_connector):
        """Test getting teams with invalid API key"""
        teams = clickup_connector.get_teams('invalid_key')

        assert isinstance(teams, list)
        assert len(teams) == 0  # Should return empty list on error


class TestClickUpSpaces:
    """Test ClickUp spaces functionality"""

    def test_get_spaces(self, clickup_connector, api_key):
        """Test getting spaces in a team"""
        # First get a team ID
        teams = clickup_connector.get_teams(api_key)

        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        assert isinstance(spaces, list)
        # Check structure if spaces exist
        if len(spaces) > 0:
            space = spaces[0]
            assert 'id' in space
            assert 'name' in space

    def test_get_spaces_invalid_team(self, clickup_connector, api_key):
        """Test getting spaces with invalid team ID"""
        spaces = clickup_connector.get_spaces(api_key, 'invalid_team_id')

        assert isinstance(spaces, list)
        assert len(spaces) == 0  # Should return empty list on error


class TestClickUpLists:
    """Test ClickUp lists functionality"""

    def test_get_lists(self, clickup_connector, api_key):
        """Test getting lists in a space"""
        # Get team and space IDs
        teams = clickup_connector.get_teams(api_key)
        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        if len(spaces) == 0:
            pytest.skip("No spaces available for testing")

        space_id = spaces[0]['id']
        lists = clickup_connector.get_lists(api_key, space_id)

        assert isinstance(lists, list)
        # Check structure if lists exist
        if len(lists) > 0:
            list_item = lists[0]
            assert 'id' in list_item
            assert 'name' in list_item


class TestClickUpTasks:
    """Test ClickUp tasks functionality"""

    def test_get_tasks(self, clickup_connector, api_key):
        """Test getting tasks in a list"""
        # Navigate to get a list ID
        teams = clickup_connector.get_teams(api_key)
        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        if len(spaces) == 0:
            pytest.skip("No spaces available for testing")

        space_id = spaces[0]['id']
        lists = clickup_connector.get_lists(api_key, space_id)

        if len(lists) == 0:
            pytest.skip("No lists available for testing")

        list_id = lists[0]['id']
        tasks = clickup_connector.get_tasks(api_key, list_id)

        assert isinstance(tasks, list)
        # Check structure if tasks exist
        if len(tasks) > 0:
            task = tasks[0]
            assert 'id' in task
            assert 'name' in task

    def test_get_task_by_id(self, clickup_connector, api_key):
        """Test getting a specific task by ID"""
        # Get a task ID first
        teams = clickup_connector.get_teams(api_key)
        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        if len(spaces) == 0:
            pytest.skip("No spaces available for testing")

        space_id = spaces[0]['id']
        lists = clickup_connector.get_lists(api_key, space_id)

        if len(lists) == 0:
            pytest.skip("No lists available for testing")

        list_id = lists[0]['id']
        tasks = clickup_connector.get_tasks(api_key, list_id)

        if len(tasks) == 0:
            pytest.skip("No tasks available for testing")

        task_id = tasks[0]['id']
        task = clickup_connector.get_task(api_key, task_id)

        assert task is not None
        assert 'id' in task
        assert 'name' in task
        assert task['id'] == task_id


class TestClickUpTaskOperations:
    """Test ClickUp task creation and updates (destructive operations)"""

    @pytest.mark.integration
    def test_create_task(self, clickup_connector, api_key):
        """Test creating a new task (integration test)"""
        # Get a list ID
        teams = clickup_connector.get_teams(api_key)
        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        if len(spaces) == 0:
            pytest.skip("No spaces available for testing")

        space_id = spaces[0]['id']
        lists = clickup_connector.get_lists(api_key, space_id)

        if len(lists) == 0:
            pytest.skip("No lists available for testing")

        list_id = lists[0]['id']

        # Create a test task
        task = clickup_connector.create_task(
            api_key,
            list_id,
            name="Test Task from API",
            description="This is a test task created by automated tests",
            priority=3  # Normal priority
        )

        assert task is not None
        assert 'id' in task
        assert task['name'] == "Test Task from API"

    @pytest.mark.integration
    def test_update_task(self, clickup_connector, api_key):
        """Test updating a task (integration test)"""
        # Get a task ID
        teams = clickup_connector.get_teams(api_key)
        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        if len(spaces) == 0:
            pytest.skip("No spaces available for testing")

        space_id = spaces[0]['id']
        lists = clickup_connector.get_lists(api_key, space_id)

        if len(lists) == 0:
            pytest.skip("No lists available for testing")

        list_id = lists[0]['id']
        tasks = clickup_connector.get_tasks(api_key, list_id)

        if len(tasks) == 0:
            pytest.skip("No tasks available for testing")

        task_id = tasks[0]['id']

        # Update the task
        updated_task = clickup_connector.update_task(
            api_key,
            task_id,
            name="Updated Task Name"
        )

        assert updated_task is not None
        assert 'id' in updated_task
        assert updated_task['name'] == "Updated Task Name"

    @pytest.mark.integration
    def test_add_comment(self, clickup_connector, api_key):
        """Test adding a comment to a task (integration test)"""
        # Get a task ID
        teams = clickup_connector.get_teams(api_key)
        if len(teams) == 0:
            pytest.skip("No teams available for testing")

        team_id = teams[0]['id']
        spaces = clickup_connector.get_spaces(api_key, team_id)

        if len(spaces) == 0:
            pytest.skip("No spaces available for testing")

        space_id = spaces[0]['id']
        lists = clickup_connector.get_lists(api_key, space_id)

        if len(lists) == 0:
            pytest.skip("No lists available for testing")

        list_id = lists[0]['id']
        tasks = clickup_connector.get_tasks(api_key, list_id)

        if len(tasks) == 0:
            pytest.skip("No tasks available for testing")

        task_id = tasks[0]['id']

        # Add a comment
        comment = clickup_connector.add_comment(
            api_key,
            task_id,
            "This is a test comment from automated tests"
        )

        assert comment is not None
        assert 'id' in comment
