def raise_error(message, params):
    exc_map = {
        'The requested branch does not exist': BranchDoesNotExistError,
        'The requested category does not exist': CategoryDoesNotExistError,
        'The requested course does not exist': CourseDoesNotExistError,
        'The requested course is already a member of this branch': CourseExistsError,
        'The requested course is already a member of this group': CourseExistsError,
        'There is no group with such key': GroupDoesNotExistError,
        'The requested group does not exist': GroupDoesNotExistError,
        'Invalid arguments provided': InvalidArgumentsError,
        'The requested API action does not exist': InvalidRequestError,
        'Your login or password is incorrect. Please try again, making sure that CAPS LOCK key is off': PasswordIncorrectError,
        'The requested unit does not exist': UnitDoesNotExistError,
        'The requested user is already a member of this branch': UserAlreadyEnrolledError,
        'The requested user is already a member of this group': UserAlreadyEnrolledError,
        'The requested user is already enrolled in this course': UserAlreadyEnrolledError,
        'A user with the same email address already exists': UserAlreadyExistsError,
        'A user with the same login already exists': UserAlreadyExistsError,
        'The requested user is no longer available': UserDeletedError,
        'The requested user does not exist': UserDoesNotExistError,
        'Your account is inactive. Please activate the account using the instructions sent to you via e-mail. If you did not receive the e-mail, check your spam folder.': UserInactiveError,
        'The requested user is not a member of this branch': UserNotEnrolledError,
        'The requested user is not a member of this group': UserNotEnrolledError,
        'The requested user is not enrolled in this course': UserNotEnrolledError,
        'User does not have a progress registered for the survey': UserNotEnrolledError,
        'User does not have a progress registered for the test': UserNotEnrolledError,
        'Password is not strong enough (should have at least (1) upper case letter, at least (1) lower case letter, at least (1) number, at least (8) characters in length)': WeakPasswordError,
    }

    e = exc_map.get(message, TalentLMSError)

    raise e(message, params)


class TalentLMSError(Exception):
    def __init__(self, msg, request_params):
        exc_msg = f'{msg} {request_params}'
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


class UserDeletedError(TalentLMSError):
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


class CourseDoesNotExistError(TalentLMSError):
    pass


class CategoryDoesNotExistError(TalentLMSError):
    pass


class GroupDoesNotExistError(TalentLMSError):
    pass


class BranchDoesNotExistError(TalentLMSError):
    pass


class UnitDoesNotExistError(TalentLMSError):
    pass
