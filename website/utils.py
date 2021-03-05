# declare utility functions here

def geti18nTag(request):
    """
    function to extract the i18n tag from a reqeust
    This function will only be working if the request holds the tag directly after the domain
    """
    print(request.path)
    return request.path.split('/')[1]