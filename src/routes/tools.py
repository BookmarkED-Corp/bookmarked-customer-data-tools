"""
Diagnostic Tools Routes

Routes for district selection, student search, and data comparison tools.
"""
from flask import Blueprint, render_template, request, jsonify, session
from src.connectors.bookmarked_db import BookmarkedDBConnector
from src.connectors.classlink import ClassLinkConnector
import structlog

logger = structlog.get_logger(__name__)

tools_bp = Blueprint('tools', __name__)


@tools_bp.route('/tools')
def tools_dashboard():
    """Display main tools dashboard with district picker"""
    return render_template('tools.html')


# Deprecated: Use /tools instead which has integrated district selector
# @tools_bp.route('/district-select')
# def district_select():
#     """Display district selection page"""
#     return render_template('district_select.html')


@tools_bp.route('/tools/student-search')
def student_search():
    """Display student search/compare tool"""
    return render_template('student_search.html')


@tools_bp.route('/tools/parent-search')
def parent_search():
    """Display parent search/compare tool"""
    return render_template('parent_search.html')


@tools_bp.route('/api/districts')
def get_districts():
    """
    Get list of districts from selected environment

    Query params:
        environment: 'staging' or 'production'
    """
    environment = request.args.get('environment', 'staging')

    try:
        # Connect to database
        db = BookmarkedDBConnector(environment=environment)

        # We'll query directly since API might not be available
        # This assumes we have a working database connection
        query = """
            SELECT id, name, "createdAt"
            FROM "District"
            ORDER BY name
        """

        # For this to work, we need to establish connection first
        # Let's assume defaults are loaded and we can connect
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # Check if it's the new nested structure
        if 'db' in env_config:
            db_config = env_config['db']
        else:
            # Old flat structure
            db_config = env_config

        # Connect to database
        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Execute query
        districts = db.execute_query(query)

        db.disconnect()

        logger.info("Districts retrieved successfully",
                   environment=environment,
                   count=len(districts))

        return jsonify({
            'success': True,
            'districts': districts
        })

    except Exception as e:
        logger.error("Error retrieving districts",
                    environment=environment,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tools_bp.route('/api/districts/<int:district_id>/classlink')
def check_classlink_data(district_id):
    """
    Check if ClassLink historical data exists for district

    Query params:
        environment: 'staging' or 'production'
    """
    environment = request.args.get('environment', 'staging')

    try:
        # Connect to database
        db = BookmarkedDBConnector(environment=environment)

        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # Check if it's the new nested structure
        if 'db' in env_config:
            db_config = env_config['db']
        else:
            db_config = env_config

        # Connect to database
        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Query for ClassLink data
        query = """
            SELECT
                cd.id,
                cd."sourcedId",
                cd.name,
                cd."lastSync",
                cd."districtId"
            FROM "ClasslinkDistrict" cd
            WHERE cd."districtId" = :district_id
            LIMIT 1
        """

        result = db.execute_query(query, {'district_id': district_id})

        db.disconnect()

        has_data = len(result) > 0
        last_sync = result[0].get('lastSync') if has_data else None

        logger.info("ClassLink data check completed",
                   district_id=district_id,
                   has_data=has_data)

        return jsonify({
            'success': True,
            'has_classlink_data': has_data,
            'last_sync': str(last_sync) if last_sync else None,
            'classlink_info': result[0] if has_data else None
        })

    except Exception as e:
        logger.error("Error checking ClassLink data",
                    district_id=district_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tools_bp.route('/api/students/<int:student_id>', methods=['GET'])
def get_student_details(student_id):
    """
    Get detailed information for a specific student by ID

    Query params:
        district_id: District ID
        environment: 'staging' or 'production'
    """
    district_id = request.args.get('district_id', type=int)
    environment = request.args.get('environment', 'staging')

    if not district_id:
        return jsonify({
            'success': False,
            'message': 'Missing district_id'
        }), 400

    try:
        # Load configuration
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # Connect to database
        db = BookmarkedDBConnector(environment=environment)

        if 'db' in env_config:
            db_config = env_config['db']
        else:
            db_config = env_config

        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Get student by ID
        student_query = """
            SELECT
                s.id,
                s."sourcedId",
                s."givenName",
                s."familyName",
                s.email,
                s.grade,
                s."isDeleted",
                s."createdAt",
                s."updatedAt"
            FROM "Student" s
            WHERE s.id = :student_id
        """

        students = db.execute_query(student_query, {'student_id': student_id})

        if not students:
            db.disconnect()
            return jsonify({
                'success': False,
                'message': 'Student not found'
            }), 404

        bookmarked_data = students[0]

        # Fetch all related data (same as search_student below)
        # Get campuses
        campus_query = """
            SELECT
                c.id,
                c.name,
                c."districtId"
            FROM "_CampusToStudent" cs
            JOIN "Campus" c ON cs."A" = c.id
            WHERE cs."B" = :student_id
            ORDER BY c.name
        """
        campuses = db.execute_query(campus_query, {'student_id': student_id})
        bookmarked_data['campuses'] = campuses

        # Get parents
        parents_query = """
            SELECT
                p.id,
                p.email,
                p."givenName",
                p."familyName",
                p.phone
            FROM "_ParentToStudent" ps
            JOIN "Parent" p ON ps."A" = p.id
            WHERE ps."B" = :student_id
            ORDER BY p."familyName", p."givenName"
        """
        parents = db.execute_query(parents_query, {'student_id': student_id})
        bookmarked_data['parents'] = parents

        # Get siblings
        siblings_query = """
            SELECT DISTINCT
                s.id,
                s."sourcedId",
                s."givenName",
                s."familyName",
                s.grade
            FROM "Student" s
            JOIN "_ParentToStudent" ps ON s.id = ps."B"
            WHERE ps."A" IN (
                SELECT "A" FROM "_ParentToStudent" WHERE "B" = :student_id
            )
            AND s.id != :student_id
            ORDER BY s.grade DESC, s."familyName", s."givenName"
        """
        siblings = db.execute_query(siblings_query, {'student_id': student_id})
        bookmarked_data['siblings'] = siblings

        # Get enrollments
        enrollments = []
        try:
            enrollment_query = """
                SELECT
                    e.id,
                    e."sourcedId",
                    e.role,
                    e.status,
                    e."beginDate",
                    e."endDate"
                FROM "OneRosterEnrollment" e
                WHERE e."userId" = :student_sourced_id
                ORDER BY e."beginDate" DESC
                LIMIT 20
            """
            enrollments = db.execute_query(enrollment_query, {
                'student_sourced_id': bookmarked_data['sourcedId']
            })
        except Exception as enrollment_error:
            logger.warning("Failed to retrieve enrollments", error=str(enrollment_error))

        # Convert dates
        for key in ['createdAt', 'updatedAt']:
            if key in bookmarked_data and bookmarked_data[key]:
                bookmarked_data[key] = str(bookmarked_data[key])

        bookmarked_data['enrollments'] = enrollments

        db.disconnect()

        # 3. Try to get enriched data from Bookmarked API (guardian account status, restrictions, checkouts)
        enriched_data = None
        if campuses and len(campuses) > 0 and 'api' in env_config:
            try:
                from src.connectors.bookmarked_api import BookmarkedAPIConnector

                api = BookmarkedAPIConnector(environment=environment)
                api_config = env_config['api']

                # Connect to API with JWT auth
                connected = api.connect(
                    base_url=api_config.get('base_url'),
                    username=api_config.get('username'),
                    password=api_config.get('password')
                )

                if connected:
                    # Use the first campus ID
                    campus_id = campuses[0]['id']

                    # Search by student ID (sourcedId)
                    enriched_response = api.get_enriched_student_data(
                        campus_id=campus_id,
                        search_query=bookmarked_data.get('sourcedId', '')
                    )

                    if enriched_response and enriched_response.get('data'):
                        # Get the first matching student from enriched data
                        enriched_students = enriched_response.get('data', [])
                        if enriched_students:
                            enriched_data = enriched_students[0]
                            logger.info("Enriched student data retrieved",
                                       student_id=student_id,
                                       restricted_books=enriched_data.get('numberOfBooksRestricted'),
                                       checkout_count=enriched_data.get('checkoutCounts'))

                    api.disconnect()
            except Exception as enriched_error:
                logger.warning("Failed to get enriched student data",
                             error=str(enriched_error))
                # Continue without enriched data

        return jsonify({
            'success': True,
            'student': True,
            'bookmarked_data': bookmarked_data,
            'enriched_data': enriched_data  # Add enriched data to response
        })

    except Exception as e:
        logger.error("Error fetching student details",
                    student_id=student_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def get_environment_config(environment):
    """Helper function to load environment configuration"""
    from src.utils.connections import ConnectionsConfig
    config_manager = ConnectionsConfig()
    defaults = config_manager.load_defaults()

    if not defaults or environment not in defaults:
        return None

    return defaults[environment]


@tools_bp.route('/api/districts/<int:district_id>/classlink-sync', methods=['GET'])
def get_district_classlink_sync(district_id):
    """
    Get ClassLink sync status for a district from Bookmarked API

    Query params:
        environment: 'staging' or 'production'
    """
    try:
        environment = request.args.get('environment', 'staging')

        logger.info("Fetching ClassLink sync status for district",
                   district_id=district_id,
                   environment=environment)

        # Get environment configuration
        env_config = get_environment_config(environment)
        if not env_config:
            return jsonify({
                'success': False,
                'message': f'No configuration found for environment: {environment}'
            }), 404

        # Check if API credentials are configured
        if 'api' not in env_config:
            logger.info("No API configuration for district",
                       district_id=district_id,
                       environment=environment)
            return jsonify({
                'success': False,
                'message': 'No API configuration found for this environment'
            }), 404

        # Connect to Bookmarked API
        from src.connectors.bookmarked_api import BookmarkedAPIConnector

        api = BookmarkedAPIConnector(environment=environment)
        api_config = env_config['api']

        connected = api.connect(
            base_url=api_config.get('base_url'),
            username=api_config.get('username'),
            password=api_config.get('password')
        )

        if not connected:
            logger.error("Failed to connect to Bookmarked API",
                        environment=environment)
            return jsonify({
                'success': False,
                'message': 'Failed to connect to Bookmarked API'
            }), 500

        # Get ClassLink sync status
        sync_status = api.get_classlink_sync_status(district_id)

        api.disconnect()

        if sync_status:
            logger.info("ClassLink sync status retrieved successfully",
                       district_id=district_id)
            return jsonify({
                'success': True,
                'sync_status': sync_status
            })
        else:
            logger.info("No ClassLink sync status available",
                       district_id=district_id)
            return jsonify({
                'success': False,
                'message': 'No ClassLink sync status available for this district'
            }), 404

    except Exception as e:
        logger.error("Error fetching ClassLink sync status",
                    district_id=district_id,
                    error=str(e),
                    exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@tools_bp.route('/api/parents/search', methods=['POST'])
def search_parent():
    """
    Search for parent in Bookmarked database

    Request body:
        search_term: Parent name or email
        district_id: Selected district ID
        environment: 'staging' or 'production'
    """
    data = request.json
    search_term = data.get('search_term')
    district_id = data.get('district_id')
    environment = data.get('environment', 'staging')

    if not search_term or not district_id:
        return jsonify({
            'success': False,
            'message': 'Missing search_term or district_id'
        }), 400

    try:
        # Load configuration
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # Connect to database
        db = BookmarkedDBConnector(environment=environment)

        # Handle nested structure
        if 'db' in env_config:
            db_config = env_config['db']
        else:
            db_config = env_config

        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Query parent from Bookmarked DB
        # Search by email, name, or phone
        parent_query = """
            SELECT DISTINCT
                p.id,
                p."sourcedId",
                p."givenName",
                p."familyName",
                p.email,
                p.phone,
                p."createdAt",
                p."updatedAt"
            FROM "Parent" p
            LEFT JOIN "_ParentToStudent" ps ON p.id = ps."A"
            LEFT JOIN "Student" s ON ps."B" = s.id
            LEFT JOIN "_CampusToStudent" cs ON s.id = cs."B"
            LEFT JOIN "Campus" c ON cs."A" = c.id
            WHERE c."districtId" = :district_id
                AND (
                    p.email ILIKE :search_term
                    OR p."givenName" ILIKE :search_term
                    OR p."familyName" ILIKE :search_term
                    OR p.phone ILIKE :search_term
                    OR CONCAT(p."givenName", ' ', p."familyName") ILIKE :search_term
                )
            ORDER BY p."familyName", p."givenName"
            LIMIT 50
        """

        parent_results = db.execute_query(parent_query, {
            'district_id': district_id,
            'search_term': f'%{search_term}%'
        })

        # If multiple parents found, return list for user to choose
        if len(parent_results) > 1:
            logger.info("Multiple parents found", count=len(parent_results))

            # Enrich each parent with child count
            for parent in parent_results:
                try:
                    child_count_query = """
                        SELECT COUNT(*) as count
                        FROM "_ParentToStudent" ps
                        WHERE ps."A" = :parent_id
                    """
                    count_result = db.execute_query(child_count_query, {
                        'parent_id': parent['id']
                    })
                    parent['child_count'] = count_result[0]['count'] if count_result else 0
                except Exception as e:
                    logger.warning("Failed to get child count", error=str(e))
                    parent['child_count'] = 0

            db.disconnect()
            return jsonify({
                'success': True,
                'multiple_matches': True,
                'count': len(parent_results),
                'parents': parent_results
            })

        parent_data = parent_results[0] if parent_results else None

        # If parent found in Bookmarked, get children
        if parent_data:
            # Get all children for this parent
            children_query = """
                SELECT
                    s.id,
                    s."sourcedId",
                    s."givenName",
                    s."familyName",
                    s.email,
                    s.grade
                FROM "_ParentToStudent" ps
                JOIN "Student" s ON ps."B" = s.id
                WHERE ps."A" = :parent_id
                ORDER BY s.grade DESC, s."familyName", s."givenName"
            """
            children = db.execute_query(children_query, {
                'parent_id': parent_data['id']
            })
            parent_data['children'] = children
            logger.info("Children retrieved for parent", count=len(children))

            # Convert date objects to strings
            for key in ['createdAt', 'updatedAt']:
                if key in parent_data and parent_data[key]:
                    parent_data[key] = str(parent_data[key])

        db.disconnect()

        # 2. Search in ClassLink snapshots (regardless of Bookmarked result)
        classlink_data = None
        classlink_error_message = None

        logger.info("Attempting ClassLink parent search",
                   district_id=district_id,
                   has_classlink_config='classlink' in defaults)

        if 'classlink' in defaults and defaults['classlink'].get('api_key'):
            logger.info("ClassLink configuration found, starting snapshot search")
            try:
                # Check if district has ClassLink integration
                classlink_query = """
                    SELECT
                        cd.id,
                        cd."sourcedId",
                        cd.name,
                        cd."lastSync",
                        cd."districtId",
                        ca.oneroster_application_id
                    FROM "ClasslinkDistrict" cd
                    LEFT JOIN "ClasslinkApplication" ca ON cd."classlinkApplicationId" = ca.id
                    WHERE cd."districtId" = :district_id
                    LIMIT 1
                """

                db_cl = BookmarkedDBConnector(environment=environment)
                connected_cl = db_cl.connect(
                    host=db_config.get('host'),
                    port=db_config.get('port', 5432),
                    database=db_config.get('database'),
                    user=db_config.get('user'),
                    password=db_config.get('password')
                )

                if connected_cl:
                    classlink_district = db_cl.execute_query(classlink_query, {'district_id': district_id})
                    db_cl.disconnect()

                    if classlink_district and len(classlink_district) > 0:
                        oneroster_app_id = classlink_district[0].get('oneroster_application_id')

                        if oneroster_app_id:
                            # Try to use snapshot data
                            from src.snapshots.snapshot_manager import SnapshotManager
                            from datetime import datetime

                            snapshot_manager = SnapshotManager()
                            today = datetime.now().strftime('%Y-%m-%d')

                            # Check if today's snapshot exists
                            snapshot = snapshot_manager.get_snapshot(district_id, today, 'classlink')

                            if snapshot and snapshot.get('status') == 'complete':
                                # Use snapshot data
                                logger.info("Using ClassLink snapshot for parent search",
                                           district_id=district_id,
                                           date=today)

                                parents = snapshot_manager.search_snapshot(
                                    district_id=district_id,
                                    date=today,
                                    source_type='classlink',
                                    entity_type='parents',
                                    search_term=search_term
                                )

                                if parents:
                                    matched_parent = parents[0]

                                    # Get children from JSONL using agents array
                                    children = snapshot_manager.get_parent_children_from_jsonl(
                                        district_id=district_id,
                                        date=today,
                                        source_type='classlink',
                                        parent_sourced_id=matched_parent.get('sourcedId')
                                    )

                                    classlink_data = {
                                        'sourcedId': matched_parent.get('sourcedId'),
                                        'givenName': matched_parent.get('givenName'),
                                        'familyName': matched_parent.get('familyName'),
                                        'email': matched_parent.get('email'),
                                        'phone': matched_parent.get('phone') or matched_parent.get('sms'),
                                        'role': matched_parent.get('role'),
                                        'status': matched_parent.get('status'),
                                        'children': children
                                    }

                                    logger.info("ClassLink parent found in snapshot",
                                               sourcedId=matched_parent.get('sourcedId'),
                                               children_count=len(children),
                                               from_snapshot=True)
                                else:
                                    classlink_error_message = 'No matching parent found in ClassLink snapshot'
                                    logger.info("No ClassLink parent match in snapshot",
                                               search_term=search_term)
                            else:
                                classlink_error_message = 'No ClassLink snapshot available for today'
                                logger.info("No snapshot available for parent search",
                                           district_id=district_id)
                        else:
                            classlink_error_message = 'District has ClassLink but no OneRoster application ID'
                    else:
                        classlink_error_message = 'District does not have ClassLink integration'

            except Exception as classlink_error:
                classlink_error_message = str(classlink_error)
                logger.error("ClassLink parent search failed",
                            district_id=district_id,
                            error=str(classlink_error))

        # Return appropriate response with both sources
        if parent_data or classlink_data:
            response = {
                'success': True,
                'parent': True,
                'bookmarked_data': parent_data,
                'classlink_data': classlink_data
            }

            # Add informative message
            if parent_data and classlink_data:
                response['message'] = 'Parent found in both Bookmarked and ClassLink'
            elif parent_data:
                response['message'] = 'Parent found in Bookmarked only'
                response['classlink_error'] = classlink_error_message
            elif classlink_data:
                response['message'] = 'Parent found in ClassLink only'

            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'message': 'No parent found in Bookmarked database or ClassLink',
                'parent': False,
                'classlink_error': classlink_error_message
            }), 404

    except Exception as e:
        logger.error("Error searching parent",
                    search_term=search_term,
                    district_id=district_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tools_bp.route('/api/parents/<int:parent_id>', methods=['GET'])
def get_parent_details(parent_id):
    """
    Get detailed information for a specific parent by ID

    Query params:
        district_id: District ID
        environment: 'staging' or 'production'
    """
    district_id = request.args.get('district_id', type=int)
    environment = request.args.get('environment', 'staging')

    if not district_id:
        return jsonify({
            'success': False,
            'message': 'Missing district_id'
        }), 400

    try:
        # Load configuration
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # Connect to database
        db = BookmarkedDBConnector(environment=environment)

        if 'db' in env_config:
            db_config = env_config['db']
        else:
            db_config = env_config

        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Get parent by ID
        parent_query = """
            SELECT
                p.id,
                p."sourcedId",
                p."givenName",
                p."familyName",
                p.email,
                p.phone,
                p."createdAt",
                p."updatedAt"
            FROM "Parent" p
            WHERE p.id = :parent_id
        """

        parents = db.execute_query(parent_query, {'parent_id': parent_id})

        if not parents:
            db.disconnect()
            return jsonify({
                'success': False,
                'message': 'Parent not found'
            }), 404

        parent_data = parents[0]

        # Get all children for this parent
        children_query = """
            SELECT
                s.id,
                s."sourcedId",
                s."givenName",
                s."familyName",
                s.email,
                s.grade
            FROM "_ParentToStudent" ps
            JOIN "Student" s ON ps."B" = s.id
            WHERE ps."A" = :parent_id
            ORDER BY s.grade DESC, s."familyName", s."givenName"
        """
        children = db.execute_query(children_query, {'parent_id': parent_id})
        parent_data['children'] = children

        # Convert dates
        for key in ['createdAt', 'updatedAt']:
            if key in parent_data and parent_data[key]:
                parent_data[key] = str(parent_data[key])

        db.disconnect()

        return jsonify({
            'success': True,
            'parent': True,
            'bookmarked_data': parent_data
        })

    except Exception as e:
        logger.error("Error fetching parent details",
                    parent_id=parent_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tools_bp.route('/api/students/<int:student_id>/parents', methods=['GET'])
def get_student_parents(student_id):
    """
    Get all parents for a specific student

    Query params:
        district_id: District ID
        environment: 'staging' or 'production'
    """
    district_id = request.args.get('district_id', type=int)
    environment = request.args.get('environment', 'staging')

    if not district_id:
        return jsonify({
            'success': False,
            'message': 'Missing district_id'
        }), 400

    try:
        # Load configuration
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # Connect to database
        db = BookmarkedDBConnector(environment=environment)

        if 'db' in env_config:
            db_config = env_config['db']
        else:
            db_config = env_config

        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Get all parents for this student
        parents_query = """
            SELECT
                p.id,
                p."sourcedId",
                p."givenName",
                p."familyName",
                p.email,
                p.phone,
                p."createdAt",
                p."updatedAt"
            FROM "_ParentToStudent" ps
            JOIN "Parent" p ON ps."A" = p.id
            WHERE ps."B" = :student_id
            ORDER BY p."familyName", p."givenName"
        """

        parents = db.execute_query(parents_query, {'student_id': student_id})

        # Convert dates
        for parent in parents:
            for key in ['createdAt', 'updatedAt']:
                if key in parent and parent[key]:
                    parent[key] = str(parent[key])

            # Get children for each parent
            children_query = """
                SELECT
                    s.id,
                    s."sourcedId",
                    s."givenName",
                    s."familyName",
                    s.email,
                    s.grade
                FROM "_ParentToStudent" ps
                JOIN "Student" s ON ps."B" = s.id
                WHERE ps."A" = :parent_id
                ORDER BY s.grade DESC, s."familyName", s."givenName"
            """
            children = db.execute_query(children_query, {'parent_id': parent['id']})
            parent['children'] = children

        db.disconnect()

        logger.info("Parents retrieved for student",
                   student_id=student_id,
                   count=len(parents))

        return jsonify({
            'success': True,
            'parents': parents
        })

    except Exception as e:
        logger.error("Error fetching parents for student",
                    student_id=student_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tools_bp.route('/api/students/search', methods=['POST'])
def search_student():
    """
    Search for student in both Bookmarked API/DB and ClassLink

    Request body:
        search_term: Student ID, name, or email
        district_id: Selected district ID
        environment: 'staging' or 'production'
    """
    data = request.json
    search_term = data.get('search_term')
    district_id = data.get('district_id')
    environment = data.get('environment', 'staging')

    if not search_term or not district_id:
        return jsonify({
            'success': False,
            'message': 'Missing search_term or district_id'
        }), 400

    try:
        # Load configuration
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if not defaults or environment not in defaults:
            return jsonify({
                'success': False,
                'message': f'No {environment} configuration found'
            }), 400

        env_config = defaults[environment]

        # 1. Search in Bookmarked Database (for enrollment data)
        db = BookmarkedDBConnector(environment=environment)

        # Handle nested structure
        if 'db' in env_config:
            db_config = env_config['db']
        else:
            db_config = env_config

        # Connect to DB
        connected = db.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 5432),
            database=db_config.get('database'),
            user=db_config.get('user'),
            password=db_config.get('password')
        )

        if not connected:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            }), 500

        # Query student from Bookmarked DB
        # First find the student(s)
        student_query = """
            SELECT DISTINCT
                s.id,
                s."sourcedId",
                s."givenName",
                s."familyName",
                s.email,
                s.grade,
                s."isDeleted",
                s."createdAt",
                s."updatedAt"
            FROM "Student" s
            LEFT JOIN "_CampusToStudent" cs ON s.id = cs."B"
            LEFT JOIN "Campus" c ON cs."A" = c.id
            WHERE c."districtId" = :district_id
                AND (
                    s."sourcedId" ILIKE :search_term
                    OR s."givenName" ILIKE :search_term
                    OR s."familyName" ILIKE :search_term
                    OR s.email ILIKE :search_term
                    OR CONCAT(s."givenName", ' ', s."familyName") ILIKE :search_term
                )
            ORDER BY s."familyName", s."givenName"
            LIMIT 50
        """

        bookmarked_results = db.execute_query(student_query, {
            'district_id': district_id,
            'search_term': f'%{search_term}%'
        })

        # If multiple students found, return the list for user to choose
        if len(bookmarked_results) > 1:
            logger.info("Multiple students found", count=len(bookmarked_results))

            # Enrich each student with enrollment count
            for student in bookmarked_results:
                try:
                    enrollment_count_query = """
                        SELECT COUNT(*) as count
                        FROM "OneRosterEnrollment" e
                        WHERE e."userId" = :student_sourced_id
                        AND e.status = 'active'
                    """
                    count_result = db.execute_query(enrollment_count_query, {
                        'student_sourced_id': student['sourcedId']
                    })
                    student['enrollment_count'] = count_result[0]['count'] if count_result else 0
                except Exception as e:
                    logger.warning("Failed to get enrollment count", error=str(e))
                    student['enrollment_count'] = 0

            db.disconnect()
            return jsonify({
                'success': True,
                'multiple_matches': True,
                'count': len(bookmarked_results),
                'students': bookmarked_results
            })

        bookmarked_data = bookmarked_results[0] if bookmarked_results else None

        # Get all campuses for this student
        if bookmarked_data:
            campus_query = """
                SELECT
                    c.id,
                    c.name,
                    c."districtId"
                FROM "_CampusToStudent" cs
                JOIN "Campus" c ON cs."A" = c.id
                WHERE cs."B" = :student_id
                ORDER BY c.name
            """
            campuses = db.execute_query(campus_query, {
                'student_id': bookmarked_data['id']
            })
            bookmarked_data['campuses'] = campuses
            logger.info("Campuses retrieved for student", count=len(campuses))

            # Get parents for this student
            parents_query = """
                SELECT
                    p.id,
                    p.email,
                    p."givenName",
                    p."familyName",
                    p.phone
                FROM "_ParentToStudent" ps
                JOIN "Parent" p ON ps."A" = p.id
                WHERE ps."B" = :student_id
                ORDER BY p."familyName", p."givenName"
            """
            parents = db.execute_query(parents_query, {
                'student_id': bookmarked_data['id']
            })
            bookmarked_data['parents'] = parents
            logger.info("Parents retrieved for student", count=len(parents))

            # Get siblings (students who share the same parents)
            siblings_query = """
                SELECT DISTINCT
                    s.id,
                    s."sourcedId",
                    s."givenName",
                    s."familyName",
                    s.grade
                FROM "Student" s
                JOIN "_ParentToStudent" ps ON s.id = ps."B"
                WHERE ps."A" IN (
                    SELECT "A" FROM "_ParentToStudent" WHERE "B" = :student_id
                )
                AND s.id != :student_id
                ORDER BY s.grade DESC, s."familyName", s."givenName"
            """
            siblings = db.execute_query(siblings_query, {
                'student_id': bookmarked_data['id']
            })
            bookmarked_data['siblings'] = siblings
            logger.info("Siblings retrieved for student", count=len(siblings))

        # Get enrollment data with class details if student found
        enrollments = []
        if bookmarked_data:
            try:
                enrollment_query = """
                    SELECT
                        e.id,
                        e."sourcedId",
                        e.role,
                        e.status,
                        e."beginDate",
                        e."endDate",
                        e."classSourcedId",
                        c.title as "className",
                        c."classCode",
                        c.subjects
                    FROM "OneRosterEnrollment" e
                    LEFT JOIN "OneRosterClass" c ON e."classSourcedId" = c."sourcedId"
                    WHERE e."userId" = :student_sourced_id
                    AND e.status = 'active'
                    ORDER BY c.title
                    LIMIT 50
                """
                enrollments = db.execute_query(enrollment_query, {
                    'student_sourced_id': bookmarked_data['sourcedId']
                })
                logger.info("Enrollments retrieved", count=len(enrollments))
            except Exception as enrollment_error:
                logger.warning("Failed to retrieve enrollments", error=str(enrollment_error))
                # Continue without enrollments

        db.disconnect()

        # Convert date objects to strings
        if bookmarked_data:
            for key in ['createdAt', 'updatedAt']:
                if key in bookmarked_data and bookmarked_data[key]:
                    bookmarked_data[key] = str(bookmarked_data[key])
            bookmarked_data['enrollments'] = enrollments

        # 2. Search in ClassLink (if configured)
        classlink_data = None
        classlink_error_message = None

        if 'classlink' in defaults and defaults['classlink'].get('api_key'):
            try:
                # First check if this district has ClassLink integration
                classlink_query = """
                    SELECT
                        cd.id,
                        cd."sourcedId",
                        cd.name,
                        cd."lastSync",
                        cd."districtId",
                        ca.oneroster_application_id
                    FROM "ClasslinkDistrict" cd
                    LEFT JOIN "ClasslinkApplication" ca ON cd."classlinkApplicationId" = ca.id
                    WHERE cd."districtId" = :district_id
                    LIMIT 1
                """

                db_cl = BookmarkedDBConnector(environment=environment)

                # Reuse the same connection config
                connected_cl = db_cl.connect(
                    host=db_config.get('host'),
                    port=db_config.get('port', 5432),
                    database=db_config.get('database'),
                    user=db_config.get('user'),
                    password=db_config.get('password')
                )

                if connected_cl:
                    classlink_district = db_cl.execute_query(classlink_query, {'district_id': district_id})
                    db_cl.disconnect()

                    if classlink_district and len(classlink_district) > 0:
                        oneroster_app_id = classlink_district[0].get('oneroster_application_id')

                        if oneroster_app_id:
                            # Try to use snapshot data first, fall back to live API
                            from src.snapshots.snapshot_manager import SnapshotManager
                            from datetime import datetime

                            snapshot_manager = SnapshotManager()
                            today = datetime.now().strftime('%Y-%m-%d')

                            # Check if today's snapshot exists
                            snapshot = snapshot_manager.get_snapshot(district_id, today, 'classlink')

                            students = []
                            parents_and_guardians = []

                            if snapshot and snapshot.get('status') == 'complete':
                                # Use snapshot data
                                logger.info("Using ClassLink snapshot for search",
                                           district_id=district_id,
                                           date=today)

                                students = snapshot_manager.search_snapshot(
                                    district_id=district_id,
                                    date=today,
                                    source_type='classlink',
                                    entity_type='students',
                                    search_term=search_term
                                )

                                # Get all parents for matching
                                parents_and_guardians = snapshot_manager.search_snapshot(
                                    district_id=district_id,
                                    date=today,
                                    source_type='classlink',
                                    entity_type='parents',
                                    search_term=''  # Get all parents
                                )

                                logger.info("Snapshot search completed",
                                           students_found=len(students),
                                           parents_loaded=len(parents_and_guardians))
                            else:
                                # Fall back to live API
                                logger.info("No snapshot available, using live ClassLink API",
                                           district_id=district_id)

                                classlink = ClassLinkConnector()
                                api_key = defaults['classlink']['api_key']

                                # Fetch all users (students AND parents) from ClassLink
                                all_users = classlink.get_users(
                                    bearer_token=api_key,
                                    oneroster_app_id=oneroster_app_id,
                                    limit=500
                                )

                                # Separate students and parents
                                all_students = [u for u in all_users if u.get('role') == 'student']
                                parents_and_guardians = [u for u in all_users if u.get('role') in ['parent', 'guardian']]

                                # Filter by search term
                                for student in all_students:
                                    student_id = student.get('sourcedId', '')
                                    given_name = student.get('givenName', '')
                                    family_name = student.get('familyName', '')
                                    email = student.get('email', '')

                                    search_lower = search_term.lower()
                                    full_name = f"{given_name} {family_name}".lower()

                                    if (search_lower in student_id.lower() or
                                        search_lower in given_name.lower() or
                                        search_lower in family_name.lower() or
                                        search_lower in email.lower() or
                                        search_lower in full_name):
                                        students.append(student)

                            # Process matched students
                            matched_student = students[0] if students else None

                            # If student found, build response with parent matching
                            if matched_student:
                                classlink_data = {
                                    'sourcedId': matched_student.get('sourcedId'),
                                    'givenName': matched_student.get('givenName'),
                                    'familyName': matched_student.get('familyName'),
                                    'email': matched_student.get('email'),
                                    'grade': matched_student.get('grade') or (matched_student.get('grades', [''])[0] if matched_student.get('grades') else None),
                                    'status': matched_student.get('status'),
                                    'identifier': matched_student.get('identifier'),
                                    'metadata': matched_student.get('metadata'),
                                    'orgs': matched_student.get('orgs', []),  # Schools
                                    'parents': []
                                }

                                # Match parents using agents array (live API) or identifier (snapshot)
                                # Note: Snapshot doesn't have agents, need to match by student identifier
                                agents = matched_student.get('agents', [])
                                if agents:
                                    parent_sourceids = [agent.get('sourcedId') for agent in agents if agent.get('type') in ['Parent', 'Guardian', 'parent', 'guardian']]

                                    # Find matching parents
                                    for parent_sourceid in parent_sourceids:
                                        parent_user = next((p for p in parents_and_guardians if p.get('sourcedId') == parent_sourceid), None)
                                        if parent_user:
                                            classlink_data['parents'].append({
                                                'sourcedId': parent_user.get('sourcedId'),
                                                'givenName': parent_user.get('givenName'),
                                                'familyName': parent_user.get('familyName'),
                                                'email': parent_user.get('email'),
                                                'phone': parent_user.get('phone') or parent_user.get('sms'),
                                                'role': parent_user.get('role')
                                            })

                                    logger.info("ClassLink parents matched",
                                               student_sourcedId=matched_student.get('sourcedId'),
                                               parent_count=len(classlink_data['parents']))

                                logger.info("ClassLink student found",
                                           sourcedId=matched_student.get('sourcedId'),
                                           from_snapshot=snapshot is not None)
                            else:
                                classlink_data = None

                            if not classlink_data:
                                classlink_error_message = 'No matching student found in ClassLink'
                                logger.info("No ClassLink student match",
                                           search_term=search_term,
                                           students_searched=len(students))
                        else:
                            classlink_error_message = 'District has ClassLink but no OneRoster application ID'
                            logger.warning("ClassLink district missing onerosterApplicationId",
                                         district_id=district_id)
                    else:
                        classlink_error_message = 'District does not have ClassLink integration'
                        logger.info("No ClassLink integration for district",
                                   district_id=district_id)

            except Exception as classlink_error:
                classlink_error_message = str(classlink_error)
                logger.error("ClassLink search failed",
                            district_id=district_id,
                            error=str(classlink_error))

        # 3. Try to get enriched data and ClassLink sync status from Bookmarked API
        enriched_data = None
        classlink_sync_status = None

        if bookmarked_data and 'campuses' in bookmarked_data and len(bookmarked_data['campuses']) > 0 and 'api' in env_config:
            try:
                from src.connectors.bookmarked_api import BookmarkedAPIConnector

                api = BookmarkedAPIConnector(environment=environment)
                api_config = env_config['api']

                # Connect to API with JWT auth
                connected = api.connect(
                    base_url=api_config.get('base_url'),
                    username=api_config.get('username'),
                    password=api_config.get('password')
                )

                if connected:
                    # Use the first campus ID
                    campus_id = bookmarked_data['campuses'][0]['id']

                    # Fetch enriched student data
                    enriched_response = api.get_enriched_student_data(
                        campus_id=campus_id,
                        search_query=bookmarked_data.get('sourcedId', '')
                    )

                    if enriched_response and enriched_response.get('data'):
                        # Get the first matching student from enriched data
                        enriched_students = enriched_response.get('data', [])
                        if enriched_students:
                            enriched_data = enriched_students[0]
                            logger.info("Enriched student data retrieved from search",
                                       sourcedId=bookmarked_data.get('sourcedId'),
                                       restricted_books=enriched_data.get('numberOfBooksRestricted'),
                                       checkout_count=enriched_data.get('checkoutCounts'))

                    # Fetch ClassLink sync status for district
                    classlink_sync_status = api.get_classlink_sync_status(district_id)
                    if classlink_sync_status:
                        logger.info("ClassLink sync status retrieved",
                                   district_id=district_id)

                    api.disconnect()
            except Exception as enriched_error:
                logger.warning("Failed to get enriched student data in search",
                             error=str(enriched_error))
                # Continue without enriched data

        # Prepare response
        if bookmarked_data:
            response = {
                'success': True,
                'student': True,
                'bookmarked_data': bookmarked_data,
                'classlink_data': classlink_data,
                'enriched_data': enriched_data,
                'classlink_sync_status': classlink_sync_status
            }

            # Include error message if ClassLink search failed but Bookmarked data exists
            if classlink_error_message:
                response['classlink_error'] = classlink_error_message

            return jsonify(response)
        else:
            response = {
                'success': False,
                'message': 'No student found in Bookmarked database',
                'student': False
            }

            # If we have ClassLink data but no Bookmarked data
            if classlink_data:
                response['success'] = True
                response['student'] = True
                response['classlink_data'] = classlink_data
                response['message'] = 'Student found in ClassLink only'

            return jsonify(response)

    except Exception as e:
        logger.error("Error searching student",
                    search_term=search_term,
                    district_id=district_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ====================
# SNAPSHOT API ROUTES
# ====================

@tools_bp.route('/api/snapshots/<int:district_id>/status', methods=['GET'])
def get_snapshot_status(district_id):
    """
    Get snapshot status for a district

    Query params:
        source_type: 'classlink' or 'oneroster'
        date: Snapshot date (YYYY-MM-DD), defaults to today
    """
    from datetime import datetime

    source_type = request.args.get('source_type', 'classlink')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    try:
        from src.snapshots.snapshot_manager import SnapshotManager

        snapshot_manager = SnapshotManager()

        # Check if snapshot exists
        snapshot = snapshot_manager.get_snapshot(district_id, date, source_type)

        if snapshot:
            logger.info("Snapshot status retrieved",
                       district_id=district_id,
                       date=date,
                       source_type=source_type,
                       status=snapshot.get('status'))

            return jsonify({
                'success': True,
                'snapshot': snapshot,
                'exists': True
            })
        else:
            # Try to get latest snapshot
            latest_snapshot = snapshot_manager.get_latest_snapshot(district_id, source_type)

            if latest_snapshot:
                logger.info("Latest snapshot found",
                           district_id=district_id,
                           date=latest_snapshot.get('snapshot_date'),
                           source_type=source_type)

                return jsonify({
                    'success': True,
                    'snapshot': latest_snapshot,
                    'exists': True,
                    'is_latest': False
                })
            else:
                logger.info("No snapshot found",
                           district_id=district_id,
                           source_type=source_type)

                return jsonify({
                    'success': True,
                    'snapshot': None,
                    'exists': False
                })

    except Exception as e:
        logger.error("Error getting snapshot status",
                    district_id=district_id,
                    error=str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tools_bp.route('/api/snapshots/<int:district_id>/refresh', methods=['POST'])
def refresh_snapshot(district_id):
    """
    Trigger snapshot refresh for a district

    Request body:
        source_type: 'classlink' or 'oneroster'
        force: Force refresh even if today's snapshot exists
        environment: 'staging' or 'production'
    """
    from datetime import datetime
    import uuid

    data = request.json or {}
    source_type = data.get('source_type', 'classlink')
    force = data.get('force', False)
    environment = data.get('environment', 'production')

    try:
        from src.snapshots.snapshot_manager import SnapshotManager
        from src.snapshots.classlink_fetcher import ClassLinkSnapshotFetcher

        snapshot_manager = SnapshotManager()
        today = datetime.now().strftime('%Y-%m-%d')

        # Check if snapshot already exists for today
        if not force:
            existing = snapshot_manager.get_snapshot(district_id, today, source_type)
            if existing and existing.get('status') == 'complete':
                logger.info("Snapshot already exists for today",
                           district_id=district_id,
                           date=today,
                           source_type=source_type)
                return jsonify({
                    'success': False,
                    'message': 'Snapshot already exists for today. Use force=true to overwrite.',
                    'snapshot': existing
                }), 400

        # Check if snapshot is currently being fetched
        if snapshot_manager.is_snapshot_in_progress(district_id, today, source_type):
            logger.warning("Snapshot fetch already in progress",
                          district_id=district_id,
                          date=today,
                          source_type=source_type)
            return jsonify({
                'success': False,
                'message': 'Snapshot fetch is already in progress for today. Please wait.'
            }), 409

        # Get ClassLink credentials
        from src.utils.connections import ConnectionsConfig
        config_manager = ConnectionsConfig()
        defaults = config_manager.load_defaults()

        if source_type == 'classlink':
            if 'classlink' not in defaults or not defaults['classlink'].get('api_key'):
                return jsonify({
                    'success': False,
                    'message': 'ClassLink API key not configured'
                }), 400

            # Get OneRoster app ID for district
            env_config = get_environment_config(environment)

            if not env_config:
                return jsonify({
                    'success': False,
                    'message': f'No configuration found for environment: {environment}'
                }), 400

            db = BookmarkedDBConnector(environment=environment)

            if 'db' in env_config:
                db_config = env_config['db']
            else:
                db_config = env_config

            connected = db.connect(
                host=db_config.get('host'),
                port=db_config.get('port', 5432),
                database=db_config.get('database'),
                user=db_config.get('user'),
                password=db_config.get('password')
            )

            if not connected:
                return jsonify({
                    'success': False,
                    'message': 'Failed to connect to database'
                }), 500

            # Get ClassLink application ID
            classlink_query = """
                SELECT
                    cd.id,
                    ca.oneroster_application_id
                FROM "ClasslinkDistrict" cd
                LEFT JOIN "ClasslinkApplication" ca ON cd."classlinkApplicationId" = ca.id
                WHERE cd."districtId" = :district_id
                LIMIT 1
            """

            classlink_district = db.execute_query(classlink_query, {'district_id': district_id})
            db.disconnect()

            if not classlink_district or len(classlink_district) == 0:
                return jsonify({
                    'success': False,
                    'message': 'District does not have ClassLink integration'
                }), 400

            oneroster_app_id = classlink_district[0].get('oneroster_application_id')

            if not oneroster_app_id:
                return jsonify({
                    'success': False,
                    'message': 'District has ClassLink but no OneRoster application ID'
                }), 400

            # Start snapshot fetch in background
            session_id = str(uuid.uuid4())
            bearer_token = defaults['classlink']['api_key']

            fetcher = ClassLinkSnapshotFetcher(snapshot_manager)
            fetcher.create_snapshot_async(
                district_id=district_id,
                bearer_token=bearer_token,
                oneroster_app_id=oneroster_app_id,
                session_id=session_id,
                date=today
            )

            logger.info("Snapshot refresh started",
                       district_id=district_id,
                       source_type=source_type,
                       session_id=session_id)

            return jsonify({
                'success': True,
                'message': 'Snapshot refresh started',
                'session_id': session_id,
                'date': today
            })

        else:
            return jsonify({
                'success': False,
                'message': f'Unsupported source type: {source_type}'
            }), 400

    except Exception as e:
        logger.error("Error refreshing snapshot",
                    district_id=district_id,
                    error=str(e),
                    exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
