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

        return jsonify({
            'success': True,
            'student': True,
            'bookmarked_data': bookmarked_data
        })

    except Exception as e:
        logger.error("Error fetching student details",
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
                            # Initialize ClassLink connector
                            classlink = ClassLinkConnector()
                            api_key = defaults['classlink']['api_key']

                            # Fetch all users (students AND parents) from ClassLink
                            # This allows us to match parents using the agents array
                            all_users = classlink.get_users(
                                bearer_token=api_key,
                                oneroster_app_id=oneroster_app_id,
                                limit=500  # Get more users to include parents
                            )

                            # Separate students and parents
                            students = [u for u in all_users if u.get('role') == 'student']
                            parents_and_guardians = [u for u in all_users if u.get('role') in ['parent', 'guardian']]

                            # Filter students by search term
                            matched_student = None
                            for student in students:
                                student_id = student.get('sourcedId', '')
                                given_name = student.get('givenName', '')
                                family_name = student.get('familyName', '')
                                email = student.get('email', '')

                                # Case-insensitive search
                                search_lower = search_term.lower()
                                full_name = f"{given_name} {family_name}".lower()

                                if (search_lower in student_id.lower() or
                                    search_lower in given_name.lower() or
                                    search_lower in family_name.lower() or
                                    search_lower in email.lower() or
                                    search_lower in full_name):

                                    matched_student = student
                                    logger.info("ClassLink student found",
                                               sourcedId=student.get('sourcedId'),
                                               oneroster_app_id=oneroster_app_id)
                                    break

                            # If student found, build response with parent matching
                            if matched_student:
                                classlink_data = {
                                    'sourcedId': matched_student.get('sourcedId'),
                                    'givenName': matched_student.get('givenName'),
                                    'familyName': matched_student.get('familyName'),
                                    'email': matched_student.get('email'),
                                    'grade': matched_student.get('grades', [''])[0] if matched_student.get('grades') else None,
                                    'status': matched_student.get('status'),
                                    'identifier': matched_student.get('identifier'),
                                    'metadata': matched_student.get('metadata'),
                                    'orgs': matched_student.get('orgs', []),  # Schools
                                    'parents': []
                                }

                                # Match parents using agents array
                                # In OneRoster, student.agents contains parent sourcedIds
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

        # Prepare response
        if bookmarked_data:
            response = {
                'success': True,
                'student': True,
                'bookmarked_data': bookmarked_data,
                'classlink_data': classlink_data
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
