# TalentLMS API

Python impormentation of the [TalentLMS API](https://www.talentlms.com/pages/docs/TalentLMS-API-Documentation.pdf).

Method names correspond one-to-one to API method names but have underscores separating words in API method names.

## Example use

```python
import talentlms

API_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

lms = talentlms.api('example.talentlms.com', API_KEY)

try:
    new_user = lms.user_signup({
        'email': 'jsmith@example.com',
        'first': 'John',
        'last': 'Smith',
        'login' 'jsmith',
        'password': 'XXXXXXXXXXXXX'
    })
    new.user.user_set_status(new_user['id'], 'active')
except talentlms.UserAlreadyExistsError:
    pass
```

## Requirements

- Python >= 2.7

## License

MIT

## Credits

Written by [Ivan Butorin](https://github.com/ib1984)
