# -*- coding: utf-8 -*-

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

    def raise_error(self, message, params):
        exc_map = {
            'The requested API action does not exist': InvalidRequestError,
            'Invalid arguments provided': InvalidArgumentsError,
            'The requested user does not exist': UserDoesNotExistError,
            'A user with the same email address already exists': UserAlreadyExistsError,
            'A user with the same login already exists': UserAlreadyExistsError,
            'The requested user is already enrolled in this course': UserAlreadyEnrolledError,
            'The requested user is not enrolled in this course': UserNotEnrolledError,
            'Password is not strong enough (should have at least (1) upper case letter, at least (1) lower case letter, at least (1) number, at least (8) characters in length)': WeakPasswordError,
            'The requested course is already a member of this branch': CourseExistsError
        }

        e = exc_map.get(message, TalentLMSError)

        raise e(message, params)

    def get(self, method, params={}):
        params_list = []

        for param, val in params.items():
            params_list.append(quote_plus(str(param)) + ':' + quote_plus(str(val), safe='@'))

        params_list.sort()
        get_params = ','.join(params_list)

        resp = requests.get('{}/{}/{}'.format(self.api_url, method, get_params),
                            auth=self.auth)
        result = json.loads(resp.text)

        if result is not None and 'error' in result:
            self.raise_error(result['error']['message'], params)

        return result

    def post(self, method, params={}):
        resp = requests.post('{}/{}'.format(self.api_url, method), data=params,
                             auth=self.auth)
        result = json.loads(resp.text)

        if result is not None and 'error' in result:
            self.raise_error(result['error']['message'], params)

        return result

    def users(self, search_term=None):
        if search_term is None:
            return self.get('users')
        elif type(search_term) == int or search_term.isdigit():
            return self.get('users', {'id': search_term})
        elif '@' in search_term:
            return self.get('users', {'email': search_term})
        else:
            return self.get('users', {'username': search_term})

    def user_login(self, args):
        raise NotImplementedError

    def user_logout(self, user_id, redirect_url=None):
        raise NotImplementedError

    def user_signup(self, user_info):
        return self.post('usersignup', user_info)

    def delete_user(self, user_id, deleted_by_user_id=None, permanent=False):
        data = {'user_id': user_id, 'permanent': ['no', 'yes'][permanent]}

        if deleted_by_user_id is not None:
            data['deleted_by_user_id'] = deleted_by_user_id

        return self.post('deleteuser', data)

    def edit_user(self, user_id, user_info):
        user_info['user_id'] = user_id
        return self.post('edituser', user_info)

    def user_set_status(self, user_id, status):
        return self.get('usersetstatus', {'user_id': user_id, 'status': status})

    def courses(self, course_id=None):
        if course_id is None:
            return self.get('courses')
        elif type(course_id) == int or course_id.isdigit():
            return self.get('courses', {'id': course_id})
        else:
            raise TypeError('course_id must be a number (int or str)')

    def create_course(self, args):
        raise NotImplementedError

    def delete_course(self, args):
        raise NotImplementedError

    def categories(self, category_id=None):
        if category_id is None:
            return self.get('categories')
        elif type(category_id) == int or category_id.isdigit():
            return self.get('categories', {'id': category_id})
        else:
            raise TypeError('category_id must be a number (int or str)')

    def groups(self, group_id=None):
        if group_id is None:
            return self.get('groups')
        elif type(group_id) == int or group_id.isdigit():
            return self.get('groups', {'id': group_id})
        else:
            raise TypeError('group_id must be a number (int or str)')

    def create_group(self, args):
        raise NotImplementedError

    def delete_group(self, args):
        raise NotImplementedError

    def branches(self, branch_id=None):
        if branch_id is None:
            return self.get('branches')
        elif type(branch_id) == int or branch_id.isdigit():
            return self.get('branches', {'id': branch_id})
        else:
            raise TypeError('branch_id must be a number (int or str)')

    def create_branch(self, args):
        raise NotImplementedError

    def delete_branch(self, args):
        raise NotImplementedError

    def branch_set_status(self, branch_id, status):
        raise NotImplementedError

    def user_forgot_username(self, email, domain_url):
        raise NotImplementedError

    def user_forgot_password(self, username, domain_url, redirect_url):
        raise NotImplementedError

    def add_user_to_course(self, user_id, course_id, role='learner'):
        return self.post('addusertocourse', {'user_id': user_id,
                                             'course_id': course_id,
                                             'role': role})

    def remove_user_from_course(self, user_id, course_id):
        return self.get('removeuserfromcourse', {'user_id': user_id,
                                                 'course_id': course_id})

    def get_user_status_in_course(self, user_id, course_id):
        return self.get('getuserstatusincourse', {'user_id': user_id,
                                                  'course_id': course_id})

    def reset_user_progress(self, user_id, course_id):
        return self.get('resetuserprogress', {'user_id': user_id,
                                              'course_id': course_id})

    def add_user_to_branch(self, user_id, branch_id):
        raise NotImplementedError

    def remove_user_from_branch(self, user_id, branch_id):
        raise NotImplementedError

    def add_course_to_branch(self, course_id, branch_id):
        return self.get('addcoursetobranch',
                        {'course_id': course_id, 'branch_id': branch_id})

    def add_user_to_group(self, user_id, group_key):
        raise NotImplementedError

    def remove_user_from_group(self, user_id, group_id):
        raise NotImplementedError

    def add_course_to_group(self, course_id, group_id):
        raise NotImplementedError

    def go_to_course(self, user_id, course_id):
        raise NotImplementedError

    def get_users_by_custom_field(self, custom_field_value):
        return self.get('getusersbycustomfield',
                        {'custom_field_value': custom_field_value})

    def get_courses_by_custom_field(self, custom_field_value):
        return self.get('getcoursesbycustomfield',
                        {'custom_field_value': custom_field_value})

    def buy_course(self, args):
        raise NotImplementedError

    def buy_category_courses(self, args):
        raise NotImplementedError

    def get_user_custom_registration_fields(self):
        custom_fields = self.get('getcustomregistrationfields')
        return {f['name']: f for f in custom_fields}

    def get_custom_course_fields(self):
        return self.get('getcustomcoursefields')

    def category_leafs_and_courses(self, category_id):
        return self.get('categoryleafsandcourses', {'id': category_id})

    def get_user_progress_in_units(self, user_id, unit_id):
        raise NotImplementedError

    def get_test_answers(self, test_id, user_id):
        raise NotImplementedError

    def get_survey_answers(self, survey_id, user_id):
        raise NotImplementedError

    def get_ilt_sessions(self, ilt_id):
        raise NotImplementedError

    def get_timeline(self, event_type):
        return self.get('gettimeline', {'event_type': event_type})

    def siteinfo(self):
        return self.get('siteinfo')

    def ratelimit(self):
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


class WeakPasswordError(TalentLMSError):
    pass


class CourseExistsError(TalentLMSError):
    pass
