import json
from urllib.parse import quote_plus

import requests

from .exceptions import raise_error


class api:
    """
    TalentLMS API Python library
    ----------------------------
    """
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
        self.auth = requests.auth.HTTPBasicAuth(api_key, '')

    def _get(self, api_method, api_params=None):
        """Send a GET API request to TalentLMS.

        Arguments:
         - api_method is an API endpoint and should not contain spaces, e.g.: 'users'
         - api_params is a dict with API request parameters

        Returns list or dict, or raises an appropriate exception.
        """
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

    def _post(self, api_method, api_params=None):
        """Send a POST API request to TalentLMS.

        Arguments:
         - api_method is an API endpoint and should not contain spaces, e.g.: 'users'
         - api_params is a dict with API request parameters

        Returns list or dict, or raises an appropriate exception.
        """
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
         - A dict with a single user's properties (if search_term defined),
           including user's courses, certifications, groups, branches, and
           badges.
         - A list of dicts with all users' abridged properties (no courses,
           certifications, groups, branches, or badges) if search_term is
           not defined.

        Example:
        >>> api.users(40457)
        {
          "id": "40457",
          "login": "john.smith",
          "first_name": "john",
          "last_name": "Smith",
          "email": "john.smith@example.org",
          "restrict_email": "1",
          "user_type": "Learner-Type",
          "timezone": "...",
          "language": "English",
          "status": "active",
          "deactivation_date": "",
          "level": "1",
          "points": "0",
          "created_on": "12/11/2015, 07:06:53",
          "last_updated": "21/08/2020, 07:05:00",
          "last_updated_timestamp": "1597989900",
          "avatar": "https://...",
          "bio": "...",
          "login_key": "https://...",
          "custom_field_1": "Company LLC",
          "custom_field_2": "on",
          "courses": [
            {
              "id": "123",
              "name": "Sample Course",
              "role": "learner",
              "enrolled_on": "15/05/2020, 04:25:35",
              "enrolled_on_timestamp": "1589513135",
              "completed_on": "",
              "completed_on_timestamp": null,
              "completion_status": "incomplete",
              "completion_percentage": "0",
              "expired_on": "",
              "expired_on_timestamp": null,
              "total_time": "3m 17s"
            },
            ...
          ],
          "branches": [
            {
              "id": "76",
              "name": "sample"
            },
            ...
          ],
          "groups": [
            {
              "id": "49",
              "name": "Sample group"
            },
            ...
          ],
          "certifications": [
            {
              "course_id": "234",
              "course_name": "Sample Certification Exam",
              "unique_id": "5c45-01a0-f1f4-7687",
              "issued_date": "06/08/2019",
              "expiration_date": "06/08/2021",
              "download_url": "https://...",
              "public_url": "https://..."
            },
            ...
          ],
          "badges": [
            {
              "name":"Activity Newbie",
              "type":"activity",
              "criteria":"4 logins",
              "issued_on":"05/11/2014, 14:44:23"
            },
            ...
          ]
        }
        """
        if search_term is None:
            return self._get('users')
        elif isinstance(search_term, int) or search_term.isdigit():
            return self._get('users', {'id': int(search_term)})
        elif '@' in search_term:
            return self._get('users', {'email': search_term})
        else:
            return self._get('users', {'username': search_term})

    def user_login(self, login, password, logout_redirect=None):
        """Create a one-time login link for a user.

        Returns a dict with 'user_id' and URL in 'login_key' or raises an
        appropriate exception:
         - UserDoesNotExistError
         - UserInactiveError
         - PasswordIncorrectError

        Example:
        >>> api.login('john.smith', 'XXXXXXXX')
        {
          "user_id": "40457",
          "login_key": "https://learn.example.com/index/autologin/key:xxxxx..."
        }
        """
        data = {'login': login, 'password': password}

        if logout_redirect is not None:
            data['logout_redirect'] = logout_redirect

        return self._post('userlogin', data)

    def user_logout(self, user_id, next_url=None):
        """Create a logout link for a user.

        Returns a dict with 'redirect_url' or raises UserDoesNotExistError. Does
        not actually logout the user until the user uses the link.

        Example:
        >>> api.user_logout(40457, 'https://www.example.com')
        {
          "redirect_url": "https://example.talentlms.com/index/logout/next:xxxx..."
        }
        """
        data = {'user_id': user_id}

        if next_url is not None:
            data['next'] = next_url

        return self._post('userlogout', data)

    def user_signup(self, first_name, last_name, email, login, password, custom_fields=None):
        """Create a user.

        Argument custom_fields is a dict with custom field names as keys.

        Returns dict with new user's properties, or raises an appropriate
        exception:
         - UserAlreadyExistsError
         - WeakPasswordError

        Example:
        >>> api.user_signup('John', 'Smith', 'jsmith@example.com', 'john.smith',
        ...                 'XXXXXXXX', {'custom_field_1': 'Company LLC'})
        {
          "id": 40457,
          "login": "john.smith",
          "first_name": "John",
          "last_name": "Smith",
          "email": "jsmith@example.com",
          "restrict_email": "0",
          "user_type": "Learner-Type",
          "timezone": "...",
          "language": "English",
          "status": "inactive",
          "level": "1",
          "points": "0",
          "created_on": "25/08/2020, 14:53:30",
          "last_updated": "25/08/2020, 14:53:30",
          "last_updated_timestamp": 1598363610,
          "avatar": "https://...",
          "bio": null,
          "login_key": "https://...",
          "custom_field_1": "Company LLC",
          "custom_field_2": "off",
        }
        """
        if custom_fields is None:
            custom_fields = {}

        return self._post('usersignup', {'first_name': first_name,
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
        {
          "message": "Operation completed successfully"
        }
        """
        data = {'user_id': int(user_id), 'permanent': ['no', 'yes'][permanent]}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self._post('deleteuser', data)

    def edit_user(self, user_id, user_info):
        """Update user properties.

        At least one of the following properties must be present in the
        user_info dict:
          first_name, last_name, email, login, password, bio, timezone, credits,
          custom_field_XXX (where XXX is the index of the custom field).

        Returns updated user properties, or raises UserDoesNotExistError.

        Example:
        >>> api.edit_user(40457, {'login': 'johnsmith'})
        {
          "id": "40457",
          "login": "johnsmith",
          "first_name": "John",
          "last_name": "Smith",
          "email": "jsmith@example.com",
          "restrict_email": "0",
          "user_type": "Learner-Type",
          "timezone": "...",
          "language": "English",
          "status": "inactive",
          "deactivation_date": "",
          "level": "1",
          "points": "0",
          "created_on": "25/08/2020, 14:53:30",
          "last_updated": "25/08/2020, 14:56:31",
          "last_updated_timestamp": 1598363791,
          "avatar": "https://...",
          "bio": null,
          "login_key": "https://...",
          "custom_field_1": "Company LLC",
          "custom_field_2": "off"
        }
        """
        if len(user_info) == 0:
            raise ValueError('user_info must have at least one property')

        return self._post('edituser', {'user_id': int(user_id), **user_info})

    def user_set_status(self, user_id, status):
        """Set user status.

        The 'status' is either 'active' or 'inactive'.

        Returns dict with 'user_id' and updated 'status', or raises an
        appropriate exception:
         - UserDoesNotExistError
         - WeakPasswordError

        Example:
        >>> api.user_set_status(40457, 'inactive')
        {
          "user_id": "40457",
          "status": "inactive"
        }
        """
        if status not in ['active', 'inactive']:
            raise ValueError(f'Invalid status: {status}. Must be "active" or "inactive"')

        return self._get('usersetstatus', {'user_id': int(user_id),
                                           'status': status})

    def courses(self, course_id=None):
        """Fetch course(s).

        Raises CourseDoesNotExistError or returns either:
         - A dict with a single course's properties, including the list of enrolled usersi, course
           units, and prerequisites (if search_term defined).
         - A list of dicts with all courses' abridged properties (no users, units, or prerequisites)
           sif search_term is not defined.

        Example:
        >>> api.courses(123)
        {
          "id": "123",
          "name": "Sample Course",
          "code": "",
          "category_id": "21",
          "description": "...",
          "price": "&#36;0.00",
          "status": "active",
          "creation_date": "21/03/2017, 07:18:23",
          "last_update_on": "13/07/2020, 11:29:44",
          "creator_id": "30",
          "hide_from_catalog": "0",
          "time_limit": "0",
          "level": null,
          "shared": "0",
          "shared_url": "",
          "avatar": "https://...",
          "big_avatar": "https://...",
          "certification": null,
          "certification_duration": null,
          "users": [
            {
              "id": "40457",
              "name": "J. Smith",
              "role": "learner",
              "enrolled_on": "24/11/2019, 09:52:37",
              "enrolled_on_timestamp": "1574589157",
              "completed_on": "",
              "completed_on_timestamp": null,
              "completion_percentage": "0",
              "expired_on": "",
              "expired_on_timestamp": null,
              "total_time": null
            },
            ...
          ],
          "units": [
            {
              "id": "3474",
              "type": "SCORM | xAPI | cmi5",
              "name": "Sample SCORM Unit",
              "url": "https://..."
            },
            ...
          ],
          "rules": [
            "All units must be completed"
          ],
          "prerequisites": [
            {
              "course_id": "234",
              "course_name": "Sample Prerequisite Course"
            },
            ...
          ]
        }
        """
        if course_id is None:
            return self._get('courses')

        return self._get('courses', {'id': int(course_id)})

    def create_course(self, name, description=None, category_id=None, **kwargs):
        """Create a course.

        Supported keyword arguments:
         - 'code' (str): course code, e.g. 'CS101'.
         - 'price' (float): price of the course.
         - 'time_limit' (int): number of days while course is active after enrollment.
         - 'creator_id' (int): id of the course author.

        Returns dict with the new course's properties.

        Example:
        >>> c = api.create_course('Sample Course', category_id=12)
        {
          "id": 123,
          "name": "Sample Course",
          "code": "",
          "category_id": "12",
          "description": "",
          "price": "&#36;0.00",
          "status": "active",
          "creation_date": "27/08/2020, 11:20:13",
          "last_update_on": "27/08/2020, 11:20:13",
          "creator_id": "1",
          "hide_from_catalog": "0",
          "time_limit": "0",
          "level": null,
          "shared": "0",
          "shared_url": "",
          "avatar": "https://...",
          "big_avatar": "https://...",
          "certification": null,
          "certification_duration": null
        }
        """
        data = {'name': name}

        if description is not None:
            data['description'] = description

        if category_id is not None:
            data['category_id'] = category_id

        allowed_kwargs = ['code', 'price', 'time_limit', 'creator_id']
        kwarg_types = {'code': str, 'price': float, 'time_limit': int, 'creator_id': int}

        for k, v in kwargs.items():
            if k not in allowed_kwargs:
                raise KeyError(f'Unknown keyword argument: {k}')
            elif v is not None:
                data[k] = kwarg_types[k](v)

        return self._post('createcourse', data)

    def delete_course(self, course_id, deleted_by_user_id=None):
        """Delete a course.

        Returns a simple message on success or raises CourseDoesNotExistError.

        Example:
        >>> api.delete_course(1)
        {
          "message": "Operation completed successfully"
        }
        """
        data = {'course_id': int(course_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self._post('deletecourse', data)

    def categories(self, category_id=None):
        """Fetch category/categories.

        Raises CategoryDoesNotExistError or returns either:
         - A dict with a single category's properties, including the courses
           (if category_id defined).
         - A list of dicts with all categories' (without courses) if
           category_id is not defined.

        Example:
        >>> api.categories(11)
        {
          "id": "12",
          "name": "Sample Category",
          "price": "&#36;0.00",
          "parent_category_id": "11",
          "courses": [
            {
              "id": "123",
              "name": "Sample Course",
              "description": "...",
              "price": "&#36;0.00",
              "status": "active",
              "hide_from_catalog": "0",
              "level": null,
              "shared": "0",
              "shared_url": "",
              "avatar": "https://...",
              "big_avatar": "https://..."
            },
            ...
          ]
        }
        """
        if category_id is None:
            return self._get('categories')

        return self._get('categories', {'id': int(category_id)})

    def groups(self, group_id=None):
        """Fetch group(s).

        Raises GroupDoesNotExistError or returns either:
         - A dict with a single groups's properties, including the group's
           users (if group_id defined).
         - A list of dicts with all groups' (without users) if group_id is not
           defined.

        Example:
        >>> api.groups(1)
        {
          "id": "1",
          "name": "Sales Staff",
          "description": "Sales Staff of Company LLC",
          "key": "xxxxxxxxx",
          "price": "&#36;0.00",
          "owner_id": "30",
          "belongs_to_branch": None,
          "max_redemptions": None,
          "redemptions_sofar": None,
          "users": [
            { "id": "12345", "name": "J. Smith" },
            ...
          ],
          "courses": [
            {
              "id": "123",
              "name": "Sample Course"
            },
            ...
          ]
        }
        """
        if group_id is None:
            return self._get('groups')

        return self._get('groups', {'id': int(group_id)})

    def create_group(self, name, description=None, key=None, **kwargs):
        """Create a group.

        The 'key' (str) argument is a group key, which users can use to join
        the group. It is recommended to set it, since 'add_user_to_group'
        requires the key to add user to a group.

        Supported keyword arguments:
         - 'price' (float): price for the group's courses.
         - 'creator_id' (int): id of the group owner/creator.
         - 'max_redemptions' (int): maximum number of user who can join the group.

        Returns a dict with the new group's properties.

        Example:
        >>> api.create_group('Sample Group', 'Sample group created from API',
                             'SAMPLE_GROUP', max_redemptions=7)
        {
          "id": 90,
          "name": "Sample Group",
          "description": "Sample group created from API",
          "key": "SAMPLE_GROUP",
          "price": "&#36;0.00",
          "owner_id": "1",
          "belongs_to_branch": null,
          "max_redemptions": "7",
          "redemptions_sofar": "0"
        }
        """
        data = {'name': name}

        if description is not None:
            data['description'] = description

        if key is not None:
            data['key'] = key

        allowed_kwargs = ['price', 'creator_id', 'max_redemptions']
        kwarg_types = {'price': float, 'creator_id': int, 'max_redemptions': int}

        for k, v in kwargs.items():
            if k not in allowed_kwargs:
                raise KeyError(f'Unknown keyword argument: {k}')
            elif v is not None:
                data[k] = kwarg_types[k](v)

        return self._post('creategroup', data)

    def delete_group(self, group_id, deleted_by_user_id=None):
        """Delete a group.

        Returns a simple message on success or raises GroupDoesNotExistError.

        Example:
        >>> api.delete_group(1)
        {
          "message": "Operation completed successfully"
        }
        """
        data = {'group_id': int(group_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self._post('deletegroup', data)

    def branches(self, branch_id=None):
        """Fetch branch(es).

        Raises BranchDoesNotExistError or returns either:
         - A dict with a single branch's properties, including its users and
           courses (if branch_id is defined).
         - A list of dicts with all branches' abridged properties (without users
           and courses) if branch_id is not defined.

        Example:
        >>> api.branches(123)
        {
          "id": "123",
          "name": "sample",
          "description": "...",
          "avatar": "https://...",
          "theme": "...",
          "badge_set_id": "1",
          "timezone": "...",
          "signup_method": "email",
          "internal_announcement": "...",
          "external_announcement": "...",
          "language": "en",
          "user_type_id": "4",
          "user_type": "Learner-Type",
          "group_id": "8",
          "registration_email_restriction": null,
          "users_limit": null,
          "disallow_global_login": "1",
          "payment_processor": "",
          "currency": "US Dollar",
          "paypal_email": "",
          "ecommerce_subscription": "0",
          "ecommerce_subscription_price": "0",
          "ecommerce_subscription_interval": "",
          "ecommerce_subscription_trial_period": "0",
          "ecommerce_credits": "0",
          "users": [
            {
              "id": "40457",
              "name": "J. Smith"
            },
            ...
          ],
          "courses": [
            {
              "id": "123",
              "name": "Sample Course"
            },
            ...
          ]
        }
        """
        if branch_id is None:
            return self._get('branches')

        return self._get('branches', {'id': int(branch_id)})

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
        {
          "message": "Operation completed successfully"
        }
        """
        data = {'branch_id': int(branch_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self._post('deletebranch', data)

    def branch_set_status(self, branch_id, status):
        """Set branch status.

        The 'status' is boolean: True - branch is activated, False - branch is
        deactivated.

        Returns dict with 'branch_id' and updated 'status', or raises
        BranchDoesNotExistError.

        Example:
        >>> api.branch_set_status(84, False)
        {
          "branch_id": "84",
          "status": "inactive"
        }
        """
        return self._get('branchsetstatus', {'branch_id': int(branch_id),
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
        [
          {
            "user_id": "40457",
            "course_id": "378",
            "role": "learner"
          }
        ]
        """
        return self._post('addusertocourse', {'user_id': int(user_id),
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
        {
          "user_id": "40457",
          "course_id": "378",
          "course_name": "Sample Course"
        }
        """
        return self._get('removeuserfromcourse', {'user_id': int(user_id),
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
        {
          "role": "learner",
          "enrolled_on": "25/12/2019, 03:58:40",
          "enrolled_on_timestamp": "1577246320",
          "completion_status": "Completed",
          "completion_percentage": "100",
          "completed_on": "25/12/2019, 03:58:50",
          "completed_on_timestamp": "1577246330",
          "expired_on": "",
          "expired_on_timestamp": None,
          "total_time": "0s",
          "units": [
            {
              "id": "3163",
              "name": "Introduction",
              "type": "SCORM | xAPI | cmi5",
              "completion_status": "Completed",
              "completed_on": "07/07/2020, 11:41:18",
              "completed_on_timestamp": "1594118478",
              "score": "",
              "total_time": "0s"
            },
            ...
          ]
        }
        """
        return self._get('getuserstatusincourse', {'user_id': int(user_id),
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
        {
          "message": "Operation completed successfully"
        }
        """
        return self._get('resetuserprogress', {'user_id': int(user_id),
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
        {
          "user_id": "123",
          "branch_id": "83",
          "branch_name": "sample"
        }
        """
        return self._get('addusertobranch', {'user_id': int(user_id),
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
        {
          "user_id": "123",
          "branch_id": "83",
          "branch_name": "sample"
        }
        """
        return self._get('removeuserfrombranch', {'user_id': int(user_id),
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
        {
          "course_id": "208",
          "branch_id": "76",
          "branch_name": "test"
        }
        """
        return self._get('addcoursetobranch', {'course_id': int(course_id),
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
        {
          "user_id": "123",
          "group_id": "83",
          "group_name": "Sample Group"
        }
        """
        return self._get('addusertogroup', {'user_id': int(user_id),
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
        {
          "user_id": "123",
          "group_id": "83",
          "group_name": "Sample Group"
        }
        """
        return self._get('removeuserfromgroup', {'user_id': int(user_id),
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
        {
          "course_id": "208",
          "group_id": "83",
          "group_name": "Sample Group"
        }
        """
        return self._get('addcoursetogroup', {'course_id': int(course_id),
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
        {
          "40457": {
            "id": "40457",
            "login": "john.smith",
            "first_name": "John",
            "last_name": "Smith",
            "email": "johnsmith@example.org",
            "status": "active",
            "language": "English",
            "deactivation_date": "",
            "created_on": "22/08/2020, 11:20:31",
            "last_updated": "23/08/2020, 05:55:01",
            "last_updated_timestamp": "1598158501",
            "certifications": []
          },
          ...
        }
        """
        return self._get('getusersbycustomfield', {'custom_field_value': custom_field_value})

    def get_courses_by_custom_field(self, custom_field_value):
        """Get all courses with custom_field_value in one of their custom
        fields."""
        return self._get('getcoursesbycustomfield', {'custom_field_value': custom_field_value})

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
        {
          "Company Name": {
            "key": "custom_field_1",
            "type": "text",
            "name": "Company Name",
            "mandatory": "yes",
            "visible_on_reports": "yes",
            "dropdown_values": "",
            "checkbox_status": "off",
            "selective_availability": "no",
            "branch": None,
            "main_domain_availability": None,
            "previous_key": None,
            "order": 1
          },
          ...
        }
        """
        custom_fields = self._get('getcustomregistrationfields')
        return {f['name']: f for f in custom_fields}

    def get_custom_course_fields(self):
        """Get all course custom fields."""
        return self._get('getcustomcoursefields')

    def category_leafs_and_courses(self, category_id):
        """Get subcategories and their courses (and courses' units) for a
        category.

        Returns a dict with subcategories as keys, or raises CategoryDoesNotExistError.

        Example:
        >>> api.category_leafs_and_courses(52)
        {
          "21": {
            "id": "21",
            "name": "Sample Sub-category",
            "price": "&#36;0.00",
            "parent_category_id": "52",
            "courses": [
              {
                "id": "17",
                "name": "Sample Course",
                "description": "...",
                "shared": "1",
                "shared_url": "https://...",
                "avatar": "https://...",
                "big_avatar": "https://...",
                "units": [ ... ]
              },
              ...
            ]
          },
          ...
        }
        """
        return self._get('categoryleafsandcourses', {'id': int(category_id)})

    def get_users_progress_in_units(self, unit_id, user_id=None):
        """Get user(s) progress in a unit.

        Returns:
         - A dict with keys ['user_id', 'status', 'score'], if 'user_id' is
           defined
         - A list of such dicts, if 'user_id' is not defined.

        Or raises an appropriate exception:
         - UserDoesNotExistError
         - UnitDoesNotExistError

        Example:
        >>> api.get_users_progress_in_units(123, 345)
        {
          "user_id": "345",
          "status": "Not attempted",
          "score": 0
        }
        """
        data = {'unit_id': int(unit_id)}

        if user_id is not None:
            data['user_id'] = user_id

        return self._get('getusersprogressinunits', data)

    def get_test_answers(self, test_id, user_id):
        """Get user's answers on a test.

        Returns a dictionary with test results (see example below), or raises
        an appropriate exception:
         - UnitDoesNotExistError
         - UserDoesNotExistError
         - UserNotEnrolledError

        >>> api.get_test_answers(5678, 1234)
        {
          "test_id": "5678",
          "test_name": "Sample Quiz",
          "user_id": "1234",
          "user_name": "John Smith",
          "score": "100.00%",
          "completion_status": "Passed",
          "completed_on": "03/05/2017, 07:50:52",
          "completed_on_timestamp": "1493794252",
          "total_time": "3m 22s",
          "questions": [
            {
              "id": "123",
              "text": "...",
              "type": "Multiple choice",
              "weight": "1",
              "correct": "1",
              "answers": {"1": "...", "2": "...", "3": "..."},
              "correct_answers": {"1": "..."},
              "user_answers": {"1": "..."}
            },
            ...
          ]
        }
        """
        return self._get('gettestanswers', {'test_id': int(test_id),
                                            'user_id': int(user_id)})

    def get_survey_answers(self, survey_id, user_id):
        """Get user's answers on a survey.

        Returns a dictionary with survey answers (see example below), or raises
        an appropriate exception:
         - UnitDoesNotExistError
         - UserDoesNotExistError
         - UserNotEnrolledError

        >>> api.get_survey_answers(123, 234)
        {
          "survey_id": "123",
          "survey_name": "Course survey",
          "user_id": "234",
          "user_name": "J. Smith",
          "completion_status": "Completed",
          "completed_on": "23/11/2018, 08:30:27",
          "completed_on_timestamp": "1542961827",
          "total_time": "1m 51s",
          "questions": [
            {
              "id": "4467",
              "text": "...",
              "type": "Multiple choice",
              "answers": {"1": "...", "2": "...", "3": "..."},
              "user_answers": {"2": "..."}
            },
            ...
          ]
        }
        """
        return self._get('getsurveyanswers', {'survey_id': int(survey_id),
                                              'user_id': int(user_id)})

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
        [
          {
            "action": "user_login_user",
            "message": "John Smith signed in",
            "timestamp": "23/08/2020, 05:58:53",
            "unix_timestamp": "1598158733",
            "user_id": "40457",
            "user_username": "john.smith",
            "user_email": "john.smith@example.org",
            "user_fullname": "John Smith",
            "object_id": "-",
            "object_name": "-",
            "secondary_object_id": "-",
            "secondary_object_name": "-",
            "event_counter": "1"
          },
          ...
        ]
        """
        if event_type not in self.events.keys():
            raise ValueError('not a valid event type: %s' % (event_type, ))

        return self._get('gettimeline', {'event_type': event_type})

    def siteinfo(self):
        """Get basic info on TalentLMS instance.

        Returns a dict with the instance properties.

        Example:
        >>> api.siteinfo()
        {
          "total_users": "1234",
          "total_courses": "123",
          "total_categories": "12",
          "total_groups": "23",
          "total_branches": "34",
          "monthly_active_users": 123,
          "signup_method": "email",
          "paypal_email": "",
          "domain_map": "learn.example.com",
          "date_format": "DDMMYYYY"
        }
        """
        return self._get('siteinfo')

    def ratelimit(self):
        """Get current API request rate limit.

        Returns a dict with hourly limit, remaining API requests, and reset
        date in UNIX timestamp and formatted formats.

        Example:
        >>> api.ratelimit()
        {
          "limit": "10000",
          "remaining": 9986,
          "reset": "1598160603",
          "formatted_reset": "23/08/2020, 06:30"
        }
        """
        return self._get('ratelimit')
