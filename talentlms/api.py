import json
from urllib.parse import quote_plus

import requests
from requests.auth import HTTPBasicAuth

from .exceptions import raise_error


class api(object):
    events = {
        'user_login_user': 'User log in',
        'user_register_user': 'User registration',
        'user_self_register': 'User self registration',
        'user_delete_user': 'User deletion',
        'user_undelete_user': 'Undelete user',
        'user_property_change': 'User update',
        'user_create_payment': 'User payment',
        'user_upgrade_level': 'User level',
        'user_unlock_badge': 'User badge',
        'course_create_course': 'Course creation',
        'course_delete_course': 'Course deletion',
        'course_undelete_course': 'Undelete course',
        'course_property_change': 'Course update',
        'course_add_user': 'Added user to course',
        'course_remove_user': 'Removed user from course',
        'course_completion': 'User completed course',
        'course_failure': 'User did not pass course',
        'course_reset_user_progress': 'Reset progress',
        'branch_create_branch': 'Branch creation',
        'branch_delete_branch': 'Branch deletion',
        'branch_property_change': 'Branch update',
        'branch_add_user': 'Added user to branch',
        'branch_remove_user': 'Removed user from branch',
        'branch_add_course': 'Added course to branch',
        'branch_remove_course': 'Removed course from branch',
        'group_create_group': 'Group creation',
        'group_delete_group': 'Group deletion',
        'group_property_change': 'Group update',
        'group_add_user': 'Added user to group',
        'group_remove_user': 'Removed user from group',
        'group_add_course': 'Added course to group',
        'group_remove_course': 'Removed course from group',
        'certification_issue_certification': 'Certification issued to user',
        'certification_refresh_certification': 'Certification renewed',
        'certification_remove_certification': 'Certification removed',
        'certification_expire_certification': 'Certification expired',
        'unitprogress_test_completion': 'Test completion',
        'unitprogress_test_failed': 'Test fail',
        'unitprogress_survey_completion': 'Survey completion',
        'unitprogress_assignment_answered': 'Assignment submission',
        'unitprogress_assignment_graded': 'Assignment grading',
        'unitprogress_ilt_graded': 'ILT grading',
        'notification_create_notification': 'Notification creation',
        'notification_delete_notification': 'Notification deletion',
        'notification_update_notification': 'Notification update',
        'automation_create_automation': 'Automation creation',
        'automation_delete_automation': 'Automation deletion',
        'automation_update_automation': 'Automation update',
        'reports_create_custom_report': 'Custom report creation',
        'reports_delete_custom_report': 'Custom report deletion',
        'reports_update_custom_report': 'Custom report update'
    }

    def __init__(self, domain, api_key, ssl=True):
        protocol = ('http', 'https')[ssl]
        self.api_url = f'{protocol}://{domain}/api/v1'
        self.auth = HTTPBasicAuth(api_key, '')

    def __get(self, api_method, api_params=None):
        """Send a GET API request to TalentLMS.

        api_method is an API endpoint and should not contain spaces, e.g.: 'users'"""
        params_list = []

        if api_params is not None:
            for param, val in api_params.items():
                params_list.append(quote_plus(str(param)) + ':' + quote_plus(str(val), safe='@'))

            params_list.sort()

        get_params = ','.join(params_list)
        resp = requests.get(f'{self.api_url}/{api_method}/{get_params}', auth=self.auth)
        result = json.loads(resp.text)

        if result is not None and 'error' in result:
            raise_error(result['error']['message'], (api_method, api_params))

        return result

    def __post(self, api_method, api_params=None):
        """Send a POST API request to TalentLMS.

        api_method is an API endpoint and should not contain spaces, e.g.: 'users'"""
        resp = requests.post(f'{self.api_url}/{api_method}', data=api_params, auth=self.auth)
        result = json.loads(resp.text)

        if result is not None and 'error' in result:
            raise_error(result['error']['message'], (api_method, api_params))

        return result

    def users(self, search_term=None):
        """Fetch users from TalentLMS.

        The search_term is treated as:
         - User ID if it is numeric (user ID).
         - Email if it is a string with '@' in it.
         - User login if it is a plain string.

        Raises UserDoesNotExistError or returns either:
         - A dict with a single user's properties (if search_term defined).
         - A list of dicts with all users' abridged properties if search_term is
           not defined.

        Examples:
        >>> api.users(40457)
        {'id': '40457', 'login': 'john.smith', 'first_name': 'John', ... }

        >>> api.users()
        [{'id': '1', 'login': ... }, ... ]
        """
        if search_term is None:
            return self.__get('users')
        elif isinstance(search_term, int) or search_term.isdigit():
            return self.__get('users', {'id': int(search_term)})
        elif '@' in search_term:
            return self.__get('users', {'email': search_term})
        else:
            return self.__get('users', {'username': search_term})

    def user_login(self, login, password, logout_redirect=None):
        """Create a one-time login link for a user.

        Returns a dict with 'user_id' and URL in 'login_key' or raises an
        appropriate exception:
         - UserDoesNotExistError
         - UserInactiveError
         - PasswordIncorrectError

        Example:
        >>> api.login('john.smith', 'XXXXXXXX')
        {'user_id': '40457',
         'login_key': 'https://learn.example.com/index/autologin/key:xxxxx...'}
        """
        data = {'login': login, 'password': password}

        if logout_redirect is not None:
            data['logout_redirect'] = logout_redirect

        return self.__post('userlogin', data)

    def user_logout(self, user_id, next_url=None):
        """Create a logout link for a user.

        Returns a dict with 'redirect_url' or raises UserDoesNotExistError. Does
        not actually logout the user until the user uses the link.

        Examples:
        >>> api.user_logout(40457, 'https://www.example.com')
        {'redirect_url': 'https://example.talentlms.com/index/logout/next:xxxx...'}
        """
        data = {'user_id': user_id}

        if next_url is not None:
            data['next'] = next_url

        return self.__post('userlogout', data)

    def user_signup(self, first_name, last_name, email, login, password, custom_fields=None):
        """Create a user.

        Argument custom_fields is a dict with custom field names as keys.

        Returns dict with new user's 'id' and other properties, or raises an
        appropriate exception:
         - UserAlreadyExistsError
         - WeakPasswordError

        Example:
        >>> api.user_signup('John', 'Smith', 'jsmith@example.com', 'john.smith',
        ...                 'XXXXXXXX', {'custom_field_1': 'Company LLC'})
        {'id': 40456, 'login': 'john.smith', 'first_name': 'John', ... }
        """
        if custom_fields is not None:
            custom_fields = {}

        return self.__post('usersignup', {'first_name': first_name,
                                          'last_name': last_name,
                                          'email': email,
                                          'login': login,
                                          'password': password,
                                          **custom_fields})

    def delete_user(self, user_id, deleted_by_user_id=None, permanent=False):
        """Delete a user.

        Returns a simple success message, or raises UserDoesNotExistError.

        Example:
        >>> api.delete_user(40456, permanent=True)
        {'message': 'Operation completed successfully'}
        """
        data = {'user_id': int(user_id), 'permanent': ['no', 'yes'][permanent]}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.__post('deleteuser', data)

    def edit_user(self, user_id, user_info):
        """Update user properties.

        At least one of the following properties must be present in the
        user_info dict:
          first_name, last_name, email, login, password, bio, timezone, credits,
          custom_field_XXX (where XXX is the index of the custom field).

        Returns updated user properties, or raises UserDoesNotExistError.

        Example:
        >>> api.edit_user(40457, {'login': 'johnsmith'})
        {'id': '40457', 'login': 'johnsmith', 'first_name': 'John', ... }
        """
        if len(user_info) == 0:
            raise ValueError('user_info must have at least one property')

        return self.__post('edituser', {'user_id': int(user_id), **user_info})

    def user_set_status(self, user_id, status):
        """Set user status.

        The 'status' is boolean: True - user is activated, False - user is
        deactivated.

        Returns dict with 'user_id' and updated 'status', or raises an
        appropriate exception:
         - UserDoesNotExistError
         - WeakPasswordError

        Example:
        >>> api.user_set_status(40457, False)
        {'user_id': '40457', 'status': 'inactive'}
        """
        return self.__get('usersetstatus', {'user_id': int(user_id),
                                            'status': ('inactive', 'active')[status]})

    def courses(self, course_id=None):
        """Fetch course(s).

        Raises CourseDoesNotExistError or returns either:
         - A dict with a single course's properties, including the list of
           enrolled users (if search_term defined).
         - A list of dicts with all courses' abridged properties if search_term
           is not defined.

        Examples:
        >>> api.courses()
        [{'id': '1', 'name': 'Introduction', 'category_id': '11', ... }, ... ]

        >>> api.courses(1)
        {'id': '1', 'name': 'Introduction', 'category_id': '11', ... }
        """
        if course_id is None:
            return self.__get('courses')
        else:
            return self.__get('courses', {'id': int(course_id)})

    def create_course(self, name, description, code=None, price=None, time_limit=None,
                      category_id=None, creator_id=None):
        """???"""
        raise NotImplementedError

    def delete_course(self, course_id, deleted_by_user_id=None):
        """Delete a course.

        Returns a simple message on success or raises CourseDoesNotExistError.

        Example:
        >>> api.delete_course(1)
        {'message': 'Operation completed successfully'}
        """
        data = {'course_id': int(course_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.__post('deletecourse', data)

    def categories(self, category_id=None):
        """Fetch category/categories.

        Raises CategoryDoesNotExistError or returns either:
         - A dict with a single category's properties, including the courses
           (if category_id defined).
         - A list of dicts with all categories' (without courses) if
           category_id is not defined.

        Examples:
        >>> api.categories(1)
        {'id': '1', 'name': 'Example category', 'price': '&#36;0.00',
         'parent_category_id': '2',
         'courses': [ {'id': '15', 'name': 'Example course', ... }, ... ] }

        >>> api.categories()
        [{'id': '1', 'name': 'Example category', 'price': '&#36;0.00',
          'parent_category_id': '2'}, ... ]
        """
        if category_id is None:
            return self.__get('categories')
        else:
            return self.__get('categories', {'id': int(category_id)})

    def groups(self, group_id=None):
        """Fetch group(s).

        Raises GroupDoesNotExistError or returns either:
         - A dict with a single groups's properties, including the group's
           users (if group_id defined).
         - A list of dicts with all groups' (without users) if group_id is not
           defined.

        Examples:
        >>> api.groups()
        [{'id': '1',
          'name': 'Sales Staff',
          'description': 'Sales Staff of Company LLC',
          'key': 'xxxxxxxxx',
          'price': '&#36;0.00',
          'owner_id': '30',
          'belongs_to_branch': None,
          'max_redemptions': None,
          'redemptions_sofar': None}, ... ]

        >>> api.groups(1)
        {'id': '1',
         'name': 'Sales Staff',
         'description': 'Sales Staff of Company LLC',
         'key': 'xxxxxxxxx',
         'price': '&#36;0.00',
         'owner_id': '30',
         'belongs_to_branch': None,
         'max_redemptions': None,
         'redemptions_sofar': None,
         'users': [{'id': '12345', 'name': 'J. Smith'}, ...] }
        """
        if group_id is None:
            return self.__get('groups')
        else:
            return self.__get('groups', {'id': int(group_id)})

    def create_group(self, name, description=None, key=None, price=None, creator_id=None, max_redemptions=None):
        """???"""
        raise NotImplementedError

    def delete_group(self, group_id, deleted_by_user_id=None):
        """Delete a group.

        Returns a simple message on success or raises GroupDoesNotExistError.

        Example:
        >>> api.delete_group(1)
        {'message': 'Operation completed successfully'}
        """
        data = {'group_id': int(group_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.__post('deletegroup', data)

    def branches(self, branch_id=None):
        """Fetch branch(es).

        Raises BranchDoesNotExistError or returns either:
         - A dict with a single branch's properties, including its users and
           courses (if branch_id is defined).
         - A list of dicts with all branches' (without users and courses) if
           branch_id is not defined.

        Examples:
        >>> api.branches()
        [{'id': '2',
          'name': 'sample',
          'description': 'Sample Branch',
          'avatar': 'https://...',
          'theme': 'Default',
          'badge_set_id': '1',
          'timezone': '(GMT -07:00) Pacific Time (US & Canada)',
          'signup_method': 'email',
          'internal_announcement': '...',
          'external_announcement': '...',
          'language': 'en',
          'user_type_id': '4',
          'user_type': 'Learner-Type',
          'group_id': '8',
          'registration_email_restriction': None,
          'users_limit': None,
          'disallow_global_login': '1',
          'payment_processor': '',
          'currency': 'US Dollar',
          'paypal_email': '',
          'ecommerce_subscription': '0',
          'ecommerce_subscription_price': '0',
          'ecommerce_subscription_interval': '',
          'ecommerce_subscription_trial_period': '0',
          'ecommerce_credits': '0'}, ... ]
        """
        if branch_id is None:
            return self.__get('branches')
        else:
            return self.__get('branches', {'id': int(branch_id)})

    def create_branch(self, name, **branch_info):
        """name
        description
        disallow_global_login
        group_id
        language
        timezone
        signup_method
        user_type
        registration_email_restriction
        users_limit
        ecommerce_processor
        currency
        paypal_email
        ecommerce_subscription
        ecommerce_subscription_price
        ecommerce_subscription_interval
        ecommerce_credits
        internal_announcement
        external_announcement
        creator_id"""
        raise NotImplementedError

    def delete_branch(self, branch_id, deleted_by_user_id=None):
        """Delete a branch.

        Returns a simple message on success or raises BranchDoesNotExistError.

        Example:
        >>> api.delete_branch(1)
        {'message': 'Operation completed successfully'}
        """
        data = {'branch_id': int(branch_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.__post('deletebranch', data)

    def branch_set_status(self, branch_id, status):
        """Set branch status.

        The 'status' is boolean: True - branch is activated, False - branch is
        deactivated.

        Returns dict with 'branch_id' and updated 'status', or raises
        BranchDoesNotExistError.

        Example:
        >>> api.branch_set_status(84, False)
        {'branch_id': '84', 'status': 'inactive'}
        """
        return self.__get('branchsetstatus', {'branch_id': int(branch_id),
                                              'status': ('inactive', 'active')[status]})

    def forgot_username(self, email, domain_url):
        """???"""
        raise NotImplementedError

    def forgot_password(self, username, domain_url, redirect_url):
        """???"""
        raise NotImplementedError

    def add_user_to_course(self, user_id, course_id, role='learner'):
        """Enroll a user to a course.

        Returns list with dict of the original API request's arguments, or
        raises one of these exceptions:
         - UserDoesNotExistError
         - CourseDoesNotExistError
         - UserAlreadyEnrolledError

        Example:
        >>> api.add_user_to_course(40457, 378)
        [{'user_id': '40457', 'course_id': '378', 'role': 'learner'}]
        """
        return self.__post('addusertocourse', {'user_id': int(user_id),
                                               'course_id': int(course_id),
                                               'role': role})

    def remove_user_from_course(self, user_id, course_id):
        """Remove a user from a course.

        Returns a dict with keys ['user_id', 'course_id', 'course_name'], or
        raises one of these exceptions:
         - UserDoesNotExistError
         - CourseDoesNotExistError
         - UserNotEnrolledError

        Example:
        >>> api.remove_user_from_course(40457, 378)
        {'user_id': '40457', 'course_id': '378', 'course_name': 'Sample Course'}
        """
        return self.__get('removeuserfromcourse', {'user_id': int(user_id),
                                                   'course_id': int(course_id)})

    def get_user_status_in_course(self, user_id, course_id):
        """Get user's status in the course.

        Returns a dict of the user's status in the course or raises an
        appropriate exception:
         - UserDoesNotExistError
         - UserNotEnrolledError
         - CourseDoesNotExistError

        Example:
        >>> api.get_user_status_in_course(3, 348)
        {'role': 'learner',
         'enrolled_on': '25/12/2019, 03:58:40',
         'enrolled_on_timestamp': '1577246320',
         'completion_status': 'Completed',
         'completion_percentage': '100',
         'completed_on': '25/12/2019, 03:58:50',
         'completed_on_timestamp': '1577246330',
         'expired_on': '',
         'expired_on_timestamp': None,
         'total_time': '0s',
         'units': [{'id': '3163',
                    'name': 'Introduction',
                    'type': 'SCORM | xAPI | cmi5',
                    'completion_status': 'Completed',
                    'completed_on': '07/07/2020, 11:41:18',
                    'completed_on_timestamp': '1594118478',
                    'score': '',
                    'total_time': '0s'}, ...]}
        """
        return self.__get('getuserstatusincourse', {'user_id': int(user_id),
                                                    'course_id': int(course_id)})

    def reset_user_progress(self, user_id, course_id):
        """Reset user's progress in the course.

        Returns a simple message on success or raises and appropriate
        exception:
         - UserDoesNotExistError
         - UserNotEnrolledError
         - CourseDoesNotExistError

        Example:
        >>> api.reset_user_progress(3, 348)
        {'message': 'Operation completed successfully'}
        """
        return self.__get('resetuserprogress', {'user_id': int(user_id),
                                                'course_id': int(course_id)})

    def add_user_to_branch(self, user_id, branch_id):
        """Add a user to a branch.

        Returns a dict with keys ['user_id', 'branch_id', 'branch_name'], or
        raises an appropriate exception:
         - UserDoesNotExistError
         - BranchDoesNotExistError
         - UserAlreadyEnrolledError

        Example:
        >>> api.add_user_to_branch(123, 83)
        {'user_id': '123', 'branch_id': '83', 'branch_name': 'sample'}
        """
        return self.__get('addusertobranch', {'user_id': int(user_id),
                                              'branch_id': int(branch_id)})

    def remove_user_from_branch(self, user_id, branch_id):
        """Remove user from a branch.

        Returns a dict with keys ['user_id', 'branch_id', 'branch_name'], or
        raises an appropriate exception:
         - UserDoesNotExistError
         - BranchDoesNotExistError
         - UserNotEnrolledError

        Example:
        >>> api.remove_user_from_branch(123, 83)
        {'user_id': '123', 'branch_id': '83', 'branch_name': 'sample'}
        """
        return self.__get('removeuserfrombranch', {'user_id': int(user_id),
                                                   'branch_id': int(branch_id)})

    def add_course_to_branch(self, course_id, branch_id):
        """Add the course to the branch.

        Returns a dict with keys ['course_id', 'branch_id', 'branch_name'] or
        raises an appropriate exception:
         - CourseDoesNotExistError
         - BranchDoesNotExistError
         - CourseExistsError

        Example:
        >>> api.add_course_to_branch(208, 76)
        {'course_id': '208', 'branch_id': '76', 'branch_name': 'test'}
        """
        return self.__get('addcoursetobranch', {'course_id': int(course_id),
                                                'branch_id': int(branch_id)})

    def add_user_to_group(self, user_id, group_key):
        """Add a user to a group.

        Returns a dict with keys ['user_id', 'group_id', 'group_name'], or
        raises an appropriate exception:
         - UserDoesNotExistError
         - GroupDoesNotExistError
         - UserAlreadyEnrolledError

        Example:
        >>> api.add_user_to_group(123, 'xxxxxxxxxxx')
        {'user_id': '123', 'group_id': '83', 'group_name': 'Sample Group'}
        """
        return self.__get('addusertogroup', {'user_id': int(user_id),
                                             'group_key': str(group_key)})

    def remove_user_from_group(self, user_id, group_id):
        """Remove a user from a group.

        Returns a dict with keys ['user_id', 'group_id', 'group_name'], or
        raises an appropriate exception:
         - UserDoesNotExistError
         - GroupDoesNotExistError
         - UserNotEnrolledError

        Example:
        >>> api.remove_user_from_group(123, 83)
        {'user_id': '123', 'group_id': '83', 'group_name': 'Sample Group'}
        """
        return self.__get('removeuserfromgroup', {'user_id': int(user_id),
                                                  'group_id': int(group_id)})

    def add_course_to_group(self, course_id, group_id):
        """Add a course to a group.

        Returns a dict with keys ['course_id', 'group_id', 'group_name'], or
        raises an appropriate exception:
         - CourseDoesNotExistError
         - GroupDoesNotExistError
         - CourseExistsError

        IMPORTANT: Group members are not automatically enrolled in the course.

        Example:
        >>> api.add_course_to_group(83, 208)
        {'course_id': '208', 'group_id': '83', 'group_name': 'Sample Group'}
        """
        return self.__get('addcoursetogroup', {'course_id': int(course_id),
                                               'group_id': int(group_id)})

    def go_to_course(self, user_id, course_id, logout_redirect=None, course_completed_redirect=None,
                     header_hidden_options=None):
        """???"""
        raise NotImplementedError

    def get_users_by_custom_field(self, custom_field_value):
        """Get all users with custom_field_value in one of their custom
        fields.

        Returns a dict with user_ids as keys and user properties dicts as
        values.

        Example:
        >>> api.get_users_by_custom_field('Company LLC')
        {'40457':
          {'id': '40457',
           'login': 'john.smith',
           'first_name': 'John',
           'last_name': 'Smith',
           'email': 'johnsmith@example.org',
           'status': 'active',
           'language': 'English',
           'deactivation_date': '',
           'created_on': '22/08/2020, 11:20:31',
           'last_updated': '23/08/2020, 05:55:01',
           'last_updated_timestamp': '1598158501',
           'certifications': []},
          ...
        }
        """
        return self.__get('getusersbycustomfield', {'custom_field_value': custom_field_value})

    def get_courses_by_custom_field(self, custom_field_value):
        """Get all courses with custom_field_value in one of their custom
        fields."""
        return self.__get('getcoursesbycustomfield', {'custom_field_value': custom_field_value})

    def buy_course(self, user_id, course_id, coupon=None):
        """???"""
        raise NotImplementedError

    def buy_category_courses(self, user_id, category_id, coupon=None):
        """???"""
        raise NotImplementedError

    def get_custom_registration_fields(self):
        """Get all user custom fields.

        Returns a dict with custom fields' names as keys, and their property
        dicts as values.

        Example:
        >>> api.get_custom_registration_fields()
        {'Company Name': {
            'key': 'custom_field_1',
            'type': 'text',
            'name': 'Company Name',
            'mandatory': 'yes',
            'visible_on_reports': 'yes',
            'dropdown_values': '',
            'checkbox_status': 'off',
            'selective_availability': 'no',
            'branch': None,
            'main_domain_availability': None,
            'previous_key': None,
            'order': 1}, ... }
        """
        custom_fields = self.__get('getcustomregistrationfields')
        return {f['name']: f for f in custom_fields}

    def get_custom_course_fields(self):
        """Get all course custom fields."""
        return self.__get('getcustomcoursefields')

    def category_leafs_and_courses(self, category_id):
        """Get subcategories and their courses (and courses' units) for a
        category.

        Returns a dict with subcategories as keys, or raises CategoryDoesNotExistError.

        Example:
        >>> api.category_leafs_and_courses(52)
        {'21': {'id': '21',
                'name': 'Sample Sub-category',
                'price': '&#36;0.00',
                'parent_category_id': '52',
                'courses': [{'id': '17',
                             'name': 'Sample Course',
                             'description': '...',
                             'shared': '1',
                             'shared_url': 'https://...',
                             'avatar': 'https://...',
                             'big_avatar': 'https://...',
                             'units': [ ... ]
                            }]
               }, ...
        }
        """
        return self.__get('categoryleafsandcourses', {'id': int(category_id)})

    def get_users_progress_in_units(self, unit_id, user_id=None):
        """Get user(s) progress in a unit.

        Returns:
         - A dict with keys ['user_id', 'status', 'score'], if 'user_id' is
           defined
         - A list of such dicts, if 'user_id' is not defined.

        Or raises an appropriate exception:
         - UserDoesNotExistError
         - UnitDoesNotExistError

        Examples:
        >>> api.get_users_progress_in_units(123, 345)
        {'user_id': '345', 'status': 'Not attempted', 'score': 0}

        >>> api.get_users_progress_in_units(123)
        [{'user_id': '345', 'status': 'Not attempted', 'score': 0}, ...]
        """
        data = {'unit_id': int(unit_id)}

        if user_id is not None:
            data['user_id'] = user_id

        return self.__get('getusersprogressinunits', data)

    def get_test_answers(self, test_id, user_id):
        """Get user's answers on a test.

        Returns a dictionary with test results (see example below), or raises
        an appropriate exception:
         - UnitDoesNotExistError
         - UserDoesNotExistError
         - UserNotEnrolledError

        >>> api.get_test_answers(5678, 1234)
        {'test_id': '5678',
         'test_name': 'Sample Quiz',
         'user_id': '1234',
         'user_name': 'John Smith',
         'score': '100.00%',
         'completion_status': 'Passed',
         'completed_on': '03/05/2017, 07:50:52',
         'completed_on_timestamp': '1493794252',
         'total_time': '3m 22s',
         'questions': [
             {'id': '123',
              'text': "...",
              'type': 'Multiple choice',
              'weight': '1',
              'correct': '1',
              'answers': {'1': '...', '2': '...', '3': '...'},
              'correct_answers': {'1': '...'},
              'user_answers': {'1': '...'}}, ... ]
        }
        """
        return self.__get('gettestanswers', {'test_id': int(test_id),
                                             'user_id': int(user_id)})

    def get_survey_answers(self, survey_id, user_id):
        """Get user's answers on a survey.

        Returns a dictionary with survey answers (see example below), or raises
        an appropriate exception:
         - UnitDoesNotExistError
         - UserDoesNotExistError
         - UserNotEnrolledError

        >>> api.get_survey_answers(123, 234)
        {'survey_id': '123',
         'survey_name': 'Course survey',
         'user_id': '234',
         'user_name': 'J. Smith',
         'completion_status': 'Completed',
         'completed_on': '23/11/2018, 08:30:27',
         'completed_on_timestamp': '1542961827',
         'total_time': '1m 51s',
         'questions': [{'id': '4467',
                        'text': '...',
                        'type': 'Multiple choice',
                        'answers': {'1': '...', '2': '...', '3': '...'},
                        'user_answers': {'2': '...'}},
                       {'id': '4470',
                        'text': '...',
                        'type': 'Free text',
                        'answers': [],
                        'user_answers': ['...']}, ... ]
        }
        """
        return self.__get('getsurveyanswers', {'survey_id': int(survey_id), 'user_id': int(user_id)})

    def get_ilt_sessions(self, ilt_id):
        """???"""
        raise NotImplementedError

    def get_timeline(self, event_type):
        """Get the last 200 events of the type event_type from the timeline.

        Available event types and their explanations are defined in api.events
        dict.

        Returns a list of dicts with event properties, or raises ValueError if
        event_type is not valid.

        Example:
        >>> api.get_timeline('user_login_user')
        [{'action': 'user_login_user',
          'message': 'John Smith signed in',
          'timestamp': '23/08/2020, 05:58:53',
          'unix_timestamp': '1598158733',
          'user_id': '40457',
          'user_username': 'john.smith',
          'user_email': 'john.smith@example.org',
          'user_fullname': 'John Smith',
          'object_id': '-',
          'object_name': '-',
          'secondary_object_id': '-',
          'secondary_object_name': '-',
          'event_counter': '1'}, ... ]
        """
        if event_type not in self.events.keys():
            raise ValueError('not a valid event type: %s' % (event_type, ))

        return self.__get('gettimeline', {'event_type': event_type})

    def siteinfo(self):
        """Get basic info on TalentLMS instance.

        Returns a dict with the instance properties.

        Example:
        >>> api.siteinfo()
        {'total_users': '1234',
         'total_courses': '123',
         'total_categories': '12',
         'total_groups': '23',
         'total_branches': '34',
         'monthly_active_users': 123,
         'signup_method': 'email',
         'paypal_email': '',
         'domain_map': 'learn.example.com',
         'date_format': 'DDMMYYYY'}
        """
        return self.__get('siteinfo')

    def ratelimit(self):
        """Get current API request rate limit.

        Returns a dict with hourly limit, remaining API requests, and reset
        date in UNIX timestamp and formatted formats.

        Example:
        >>> api.ratelimit()
        {'limit': '10000',
         'remaining': 9986,
         'reset': '1598160603',
         'formatted_reset': '23/08/2020, 06:30'}
        """
        return self.__get('ratelimit')
