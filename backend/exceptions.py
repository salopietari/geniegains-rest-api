class PasswordTooShortError(Exception):
    pass

class PasswordsDoNotMatchError(Exception):
    pass

class UsernameAlreadyExistsError(Exception):
    pass

class EmailAlreadyExistsError(Exception):
    pass

class QueryQuotaExceededError(Exception):
    pass