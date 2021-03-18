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