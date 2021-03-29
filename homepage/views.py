from django.shortcuts import render

from website.utils import get_i18n_tag


# Create your views here.

def startpage(request):
    """
    view for displaying the index page
    to prevent translation chaos this view is split into two templates - one for de and one for en
    """

    if get_i18n_tag(request) == 'de':
        return render(request, "homepage/startpage_de.html")
    else:
        return render(request, "homepage/startpage_en.html")
