"""
HubSpot API Connector

Handles authentication and API calls to HubSpot for ticket management.
"""
import os
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException
import structlog

logger = structlog.get_logger(__name__)


class HubSpotConnector:
    """Connector for HubSpot API"""

    def __init__(self):
        """Initialize HubSpot connector"""
        self.api_url = os.getenv('HUBSPOT_API_URL', 'https://api.hubapi.com')
        self.access_token = None

    def test_connection(self, access_token: str) -> Dict[str, Any]:
        """
        Test HubSpot API connection with access token

        Args:
            access_token: HubSpot API access token

        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            # Test with account info endpoint
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.api_url}/account-info/v3/details',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                account_data = response.json()
                logger.info("HubSpot connection test successful",
                           portal_id=account_data.get('portalId'))

                return {
                    'success': True,
                    'message': 'Connection successful',
                    'details': {
                        'portal_id': account_data.get('portalId'),
                        'time_zone': account_data.get('timeZone'),
                        'currency': account_data.get('currency')
                    }
                }
            else:
                logger.error("HubSpot connection test failed",
                           status_code=response.status_code,
                           response=response.text[:200])

                return {
                    'success': False,
                    'message': f'API returned status {response.status_code}',
                    'details': None
                }

        except RequestException as e:
            logger.error("HubSpot connection test failed",
                        error=str(e))
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'details': None
            }
        except Exception as e:
            logger.error("Unexpected error testing HubSpot connection",
                        error=str(e))
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'details': None
            }

    def connect(self, access_token: str) -> bool:
        """
        Set HubSpot access token

        Args:
            access_token: HubSpot API access token

        Returns:
            True if token is valid
        """
        result = self.test_connection(access_token)
        if result['success']:
            self.access_token = access_token
            logger.info("HubSpot connector configured")
            return True
        return False

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a ticket by ID

        Args:
            ticket_id: HubSpot ticket ID

        Returns:
            Ticket data or None if not found
        """
        if not self.access_token:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.api_url}/crm/v3/objects/tickets/{ticket_id}',
                headers=headers,
                params={'properties': 'subject,content,hs_ticket_priority'},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("Failed to get ticket",
                             ticket_id=ticket_id,
                             status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error getting ticket",
                        ticket_id=ticket_id,
                        error=str(e))
            return None

    def add_note_to_ticket(self, ticket_id: str, note: str) -> bool:
        """
        Add a note to a ticket

        Args:
            ticket_id: HubSpot ticket ID
            note: Note text

        Returns:
            True if successful
        """
        if not self.access_token:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            # Create engagement (note)
            data = {
                'engagement': {
                    'active': True,
                    'type': 'NOTE'
                },
                'associations': {
                    'ticketIds': [int(ticket_id)]
                },
                'metadata': {
                    'body': note
                }
            }

            response = requests.post(
                f'{self.api_url}/engagements/v1/engagements',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info("Note added to ticket",
                           ticket_id=ticket_id)
                return True
            else:
                logger.error("Failed to add note to ticket",
                           ticket_id=ticket_id,
                           status_code=response.status_code,
                           response=response.text[:200])
                return False

        except Exception as e:
            logger.error("Error adding note to ticket",
                        ticket_id=ticket_id,
                        error=str(e))
            return False
