from authentication.models import User

from datetime import timedelta
import re


# declare utility functions here

def get_i18n_tag(request):
    """
    function to extract the i18n tag from a request
    This function will only be working if the request holds the tag directly after the domain
    """
    return request.path.split('/')[1]


def get_test_user():
    """
    returns the test user which is used when a user is needed for testing purposes
    creates the test user if it does not exit
    """
    return User.objects.get_or_create(email='test@test.de', first_name='Test', last_name="Tester", is_active=False)[0]


def get_timedelta(string):
    """
    convert a string in the format [num days]d[num hours]h[num minutes]m[num seconds]s
    if not possible return None
    """
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parms = regex.match(string)
    
    args = dict()
    for (name, parm) in parms.groupdict().items():
        if parm:
            args[name] = int(parm)
    if len(args) < 1:
        return None
    return timedelta(**args)
