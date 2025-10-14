"""
ClickUp API Connector

Connector for ClickUp project management platform.
"""
import requests
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ClickUpConnector:
    """Connector for ClickUp API"""

    def __init__(self, api_url: str = 'https://api.clickup.com/api/v2'):
        """
        Initialize ClickUp connector

        Args:
            api_url: Base URL for ClickUp API
        """
        self.api_url = api_url.rstrip('/')

    def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Test ClickUp API connection with provided API key

        Args:
            api_key: ClickUp API key

        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            headers = {
                'Authorization': api_key,
                'Content-Type': 'application/json'
            }

            # Test connection by getting authorized user info
            response = requests.get(
                f'{self.api_url}/user',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()
                user_info = user_data.get('user', {})

                logger.info("ClickUp connection test successful",
                           user_id=user_info.get('id'),
                           username=user_info.get('username'))

                return {
                    'success': True,
                    'message': 'Connected to ClickUp successfully',
                    'details': {
                        'user_id': user_info.get('id'),
                        'username': user_info.get('username'),
                        'email': user_info.get('email'),
                        'color': user_info.get('color')
                    }
                }
            else:
                logger.error("ClickUp connection test failed",
                            status_code=response.status_code,
                            response=response.text[:200])

                return {
                    'success': False,
                    'message': f'Connection failed: {response.status_code} - {response.text[:100]}',
                    'details': None
                }

        except requests.exceptions.Timeout:
            logger.error("ClickUp connection timeout")
            return {
                'success': False,
                'message': 'Connection timeout - ClickUp API did not respond',
                'details': None
            }
        except requests.exceptions.RequestException as e:
            logger.error("ClickUp connection request failed", error=str(e))
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'details': None
            }
        except Exception as e:
            logger.error("Unexpected error testing ClickUp connection", error=str(e))
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'details': None
            }

    def get_teams(self, api_key: str) -> List[Dict]:
        """
        Get all teams (workspaces) the user has access to

        Args:
            api_key: ClickUp API key

        Returns:
            List of team dictionaries
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'{self.api_url}/team',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('teams', [])
            else:
                logger.error("Failed to get ClickUp teams",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClickUp teams", error=str(e))
            return []

    def get_spaces(self, api_key: str, team_id: str) -> List[Dict]:
        """
        Get all spaces in a team

        Args:
            api_key: ClickUp API key
            team_id: Team ID

        Returns:
            List of space dictionaries
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'{self.api_url}/team/{team_id}/space',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('spaces', [])
            else:
                logger.error("Failed to get ClickUp spaces",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClickUp spaces", error=str(e))
            return []

    def get_lists(self, api_key: str, space_id: str) -> List[Dict]:
        """
        Get all lists in a space

        Args:
            api_key: ClickUp API key
            space_id: Space ID

        Returns:
            List of list dictionaries
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'{self.api_url}/space/{space_id}/list',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('lists', [])
            else:
                logger.error("Failed to get ClickUp lists",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClickUp lists", error=str(e))
            return []

    def get_tasks(self, api_key: str, list_id: str,
                  archived: bool = False) -> List[Dict]:
        """
        Get all tasks in a list

        Args:
            api_key: ClickUp API key
            list_id: List ID
            archived: Include archived tasks

        Returns:
            List of task dictionaries
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        params = {
            'archived': str(archived).lower()
        }

        try:
            response = requests.get(
                f'{self.api_url}/list/{list_id}/task',
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('tasks', [])
            else:
                logger.error("Failed to get ClickUp tasks",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClickUp tasks", error=str(e))
            return []

    def get_task(self, api_key: str, task_id: str) -> Optional[Dict]:
        """
        Get a specific task by ID

        Args:
            api_key: ClickUp API key
            task_id: Task ID

        Returns:
            Task dictionary or None
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'{self.api_url}/task/{task_id}',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Failed to get ClickUp task",
                            task_id=task_id,
                            status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error getting ClickUp task", task_id=task_id, error=str(e))
            return None

    def create_task(self, api_key: str, list_id: str,
                   name: str, description: str = None,
                   assignees: List[int] = None,
                   priority: int = None,
                   status: str = None) -> Optional[Dict]:
        """
        Create a new task in a list

        Args:
            api_key: ClickUp API key
            list_id: List ID to create task in
            name: Task name
            description: Task description
            assignees: List of assignee user IDs
            priority: Priority (1=urgent, 2=high, 3=normal, 4=low)
            status: Status name

        Returns:
            Created task dictionary or None
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        data = {'name': name}
        if description:
            data['description'] = description
        if assignees:
            data['assignees'] = assignees
        if priority:
            data['priority'] = priority
        if status:
            data['status'] = status

        try:
            response = requests.post(
                f'{self.api_url}/list/{list_id}/task',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Created ClickUp task", list_id=list_id, task_name=name)
                return response.json()
            else:
                logger.error("Failed to create ClickUp task",
                            status_code=response.status_code,
                            response=response.text[:200])
                return None

        except Exception as e:
            logger.error("Error creating ClickUp task", error=str(e))
            return None

    def update_task(self, api_key: str, task_id: str, **kwargs) -> Optional[Dict]:
        """
        Update a task

        Args:
            api_key: ClickUp API key
            task_id: Task ID to update
            **kwargs: Fields to update (name, description, status, priority, etc.)

        Returns:
            Updated task dictionary or None
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.put(
                f'{self.api_url}/task/{task_id}',
                headers=headers,
                json=kwargs,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Updated ClickUp task", task_id=task_id)
                return response.json()
            else:
                logger.error("Failed to update ClickUp task",
                            task_id=task_id,
                            status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error updating ClickUp task", task_id=task_id, error=str(e))
            return None

    def add_comment(self, api_key: str, task_id: str, comment_text: str) -> Optional[Dict]:
        """
        Add a comment to a task

        Args:
            api_key: ClickUp API key
            task_id: Task ID
            comment_text: Comment text

        Returns:
            Comment dictionary or None
        """
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'comment_text': comment_text
        }

        try:
            response = requests.post(
                f'{self.api_url}/task/{task_id}/comment',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Added comment to ClickUp task", task_id=task_id)
                return response.json()
            else:
                logger.error("Failed to add comment to ClickUp task",
                            task_id=task_id,
                            status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error adding comment to ClickUp task", task_id=task_id, error=str(e))
            return None
