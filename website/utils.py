from authentication.models import User

# declare utility functions here

def geti18nTag(request):
    """
    function to extract the i18n tag from a reqeust
    This function will only be working if the request holds the tag directly after the domain
    """
    return request.path.split('/')[1]


def geti18nTagClosestToRequest(request):
    try:
        if request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0] == 'de':
            return 'de'
    except:
        pass
    return 'en'

def getTestUser():
    """
    returns the test user which is used when a user is needed for testing purposes
    creates the test user if it does not exit
    """
    return User.objects.get_or_create(email='test@test.de', first_name='Test', last_name="Tester", is_active=False)[0]