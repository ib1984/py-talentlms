
import json

import requests
from requests.auth import HTTPBasicAuth

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus


class api(object):
    def __init__(self, domain, api_key, ssl=True):
        self.domain = domain
        self.ssl = ssl
        self.api_url = '{}://{}/api/v1'.format(['http', 'https'][ssl], domain)
        self.auth = HTTPBasicAuth(api_key, '')

    def get(self, api_method, api_params={}):
        """Send a GET API request to TalentLMS.

        api_method is an API endpoint and should not contain spaces, e.g.: 'users'"""
        params_list = []

        for param, val in api_params.items():
            params_list.append(quote_plus(str(param)) + ':' + quote_plus(str(val), safe='@'))

        params_list.sort()
        get_params = ','.join(params_list)

        resp = requests.get('{}/{}/{}'.format(self.api_url, api_method, get_params),
                            auth=self.auth)
        result = json.loads(resp.text)

        if result is not None and 'error' in result:
            raise_error(result['error']['message'], api_params)

        return result

    def post(self, api_method, api_params={}):
        """Send a POST API request to TalentLMS.

        api_method is an API endpoint and should not contain spaces, e.g.: 'users'"""
        resp = requests.post('{}/{}'.format(self.api_url, api_method), data=api_params,
                             auth=self.auth)
        result = json.loads(resp.text)

        if result is not None and 'error' in result:
            raise_error(result['error']['message'], api_params)

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
            return self.get('users')
        elif isinstance(search_term, int) or search_term.isdigit():
            return self.get('users', {'id': int(search_term)})
        elif '@' in search_term:
            return self.get('users', {'email': search_term})
        else:
            return self.get('users', {'username': search_term})

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

        return self.post('userlogin', data)

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

        return self.post('userlogout', data)

    def user_signup(self, first_name, last_name, email, login, password, custom_fields={}):
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
        return self.post('usersignup', {'first_name': first_name,
                                        'last_name': last_name,
                                        'email': email,
                                        'login': login,
                                        'password': password,
                                        **custom_fields
                                        })

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

        return self.post('deleteuser', data)

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

        return self.post('edituser', {'user_id': int(user_id), **user_info})

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
        return self.get('usersetstatus', {'user_id': int(user_id),
                                          'status': ('inactive', 'active')[status]})

    def courses(self, course_id=None):
        """Fetch course(s).

        Returns a single course if course_id is set. Otherwise returns all
        courses.
        """
        if course_id is None:
            return self.get('courses')
        else:
            return self.get('courses', {'id': int(course_id)})

    def create_course(self, name, description, code=None, price=None,
                      time_limit=None, category_id=None, creator_id=None):
        """???"""
        raise NotImplementedError

    def delete_course(self, course_id, deleted_by_user_id=None):
        """Delete a course."""
        data = {'course_id': int(course_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.post('deletecourse', data)

    def categories(self, category_id=None):
        """Fetch category/categories.

        Returns a single category if category_id is defined. Otherwise
        returns all categories."""
        if category_id is None:
            return self.get('categories')
        else:
            return self.get('categories', {'id': int(category_id)})

    def groups(self, group_id=None):
        """Fetch group(s).

        Returns a single group if group_id is defined. Otherwise returns all
        groups."""
        if group_id is None:
            return self.get('groups')
        else:
            return self.get('groups', {'id': int(group_id)})

    def create_group(self, name, description=None, key=None, price=None,
                     creator_id=None, max_redemptions=None):
        """???"""
        raise NotImplementedError

    def delete_group(self, group_id, deleted_by_user_id=None):
        """Delete a group."""
        data = {'course_id': int(group_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.post('deletegroup', data)

    def branches(self, branch_id=None):
        """Fetch branch(es).

        Returns a single branch if branch_id is defined. Otherwise returns all
        branches."""
        if branch_id is None:
            return self.get('branches')
        else:
            return self.get('branches', {'id': int(branch_id)})

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
        """Delete a branch."""
        data = {'course_id': int(branch_id)}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = int(deleted_by_user_id)

        return self.post('deletebranch', data)

    def branch_set_status(self, branch_id, status):
        """???"""
        raise NotImplementedError

    def forgot_username(self, email, domain_url):
        """???"""
        raise NotImplementedError

    def forgot_password(self, username, domain_url, redirect_url):
        """???"""
        raise NotImplementedError

    def add_user_to_course(self, user_id, course_id, role='learner'):
        """Add a user to the course."""
        return self.post('addusertocourse', {'user_id': int(user_id),
                                             'course_id': int(course_id),
                                             'role': role})

    def remove_user_from_course(self, user_id, course_id):
        """Remove the user from a course."""
        return self.get('removeuserfromcourse', {'user_id': int(user_id),
                                                 'course_id': int(course_id)})

    def get_user_status_in_course(self, user_id, course_id):
        """Get user's status in the course."""
        return self.get('getuserstatusincourse', {'user_id': int(user_id),
                                                  'course_id': int(course_id)})

    def reset_user_progress(self, user_id, course_id):
        """Reset user's progress in the course."""
        return self.get('resetuserprogress', {'user_id': int(user_id),
                                              'course_id': int(course_id)})

    def add_user_to_branch(self, user_id, branch_id):
        """???"""
        raise NotImplementedError

    def remove_user_from_branch(self, user_id, branch_id):
        """???"""
        raise NotImplementedError

    def add_course_to_branch(self, course_id, branch_id):
        """Add the course to the branch."""
        return self.get('addcoursetobranch', {'course_id': int(course_id),
                                              'branch_id': int(branch_id)})

    def add_user_to_group(self, user_id, group_key):
        """???"""
        raise NotImplementedError

    def remove_user_from_group(self, user_id, group_id):
        """???"""
        raise NotImplementedError

    def add_course_to_group(self, course_id, group_id):
        """???"""
        raise NotImplementedError

    def go_to_course(self, user_id, course_id, logout_redirect=None,
                     course_completed_redirect=None,
                     header_hidden_options=None):
        """???"""
        raise NotImplementedError

    def get_users_by_custom_field(self, custom_field_value):
        """Get all users with custom_field_value in one of their custom
        fields."""
        return self.get('getusersbycustomfield',
                        {'custom_field_value': custom_field_value})

    def get_courses_by_custom_field(self, custom_field_value):
        """Get all courses with custom_field_value in one of their custom
        fields."""
        return self.get('getcoursesbycustomfield',
                        {'custom_field_value': custom_field_value})

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
        custom_fields = self.get('getcustomregistrationfields')
        return {f['name']: f for f in custom_fields}

    def get_custom_course_fields(self):
        """Get all course custom fields."""
        return self.get('getcustomcoursefields')

    def category_leafs_and_courses(self, category_id):
        """???"""
        return self.get('categoryleafsandcourses', {'id': int(category_id)})

    def get_user_progress_in_units(self, user_id, unit_id):
        """???"""
        raise NotImplementedError

    def get_test_answers(self, test_id, user_id):
        """???"""
        raise NotImplementedError

    def get_survey_answers(self, survey_id, user_id):
        """???"""
        raise NotImplementedError

    def get_ilt_sessions(self, ilt_id):
        """???"""
        raise NotImplementedError

    def get_timeline(self, event_type):
        """Get the last 200 events of the type event_type from the timeline."""
        return self.get('gettimeline', {'event_type': event_type})

    def siteinfo(self):
        """???"""
        return self.get('siteinfo')

    def ratelimit(self):
        """???"""
        return self.get('ratelimit')


class TalentLMSError(Exception):
    def __init__(self, msg, request_params):
        exc_msg = '{} {}'.format(msg, request_params)
        super(TalentLMSError, self).__init__(exc_msg)
        self.message = msg
        self.request_params = request_params


class InvalidRequestError(TalentLMSError):
    pass


class InvalidArgumentsError(TalentLMSError):
    pass


class UserAlreadyExistsError(TalentLMSError):
    pass


class UserAlreadyEnrolledError(TalentLMSError):
    pass


class UserNotEnrolledError(TalentLMSError):
    pass


class UserDoesNotExistError(TalentLMSError):
    pass


class UserInactiveError(TalentLMSError):
    pass


class WeakPasswordError(TalentLMSError):
    pass


class PasswordIncorrectError(TalentLMSError):
    pass


class CourseExistsError(TalentLMSError):
    pass


def raise_error(message, params):
    exc_map = {
        'The requested API action does not exist': InvalidRequestError,
        'Invalid arguments provided': InvalidArgumentsError,
        'The requested user does not exist': UserDoesNotExistError,
        'A user with the same email address already exists': UserAlreadyExistsError,
        'A user with the same login already exists': UserAlreadyExistsError,
        'The requested user is already enrolled in this course': UserAlreadyEnrolledError,
        'The requested user is not enrolled in this course': UserNotEnrolledError,
        'Password is not strong enough (should have at least (1) upper case letter, at least (1) lower case letter, at least (1) number, at least (8) characters in length)': WeakPasswordError,
        'The requested course is already a member of this branch': CourseExistsError,
        'Your account is inactive. Please activate the account using the instructions sent to you via e-mail. If you did not receive the e-mail, check your spam folder.': UserInactiveError,
        'Your login or password is incorrect. Please try again, making sure that CAPS LOCK key is off': PasswordIncorrectError
    }

    e = exc_map.get(message, TalentLMSError)

    raise e(message, params)

