from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm
from psucontrol.models import PSU, PendingPSU, DataMeasurement


# Create your views here.

@csrf_exempt
@login_required
def register_psu_view(request):
    """
    view for setting up a new psu and converting a PendingPSU in a PSU
    """

    @csrf_protect
    def create_psu(request, form):
        # get the corresponding PendingPSU
        p_psu = PendingPSU.objects.get(pairing_key=form.cleaned_data['pairing_key'])
        # create new PSU
        PSU(name=form.cleaned_data['name'], identity_key=p_psu.identity_key,
            public_rsa_key=p_psu.public_rsa_key, owner=request.user).save()
        # delete PendingPSU
        p_psu.delete()
        messages.success(request, _('Successfully registered your new Plant Supply Unit.'))

    form = RegisterPSUForm(request.POST or None)

    # check whether form was submitted correctly
    if request.POST and form.is_valid():
        create_PSU(request, form)
    
    return render(request, 'psufrontend/register_psu.html', {'form':form})

@login_required
def table_view(request):
    """
    view to handle the tabular-style presentation of measurements
    this view is used to be refered to in links, etc.
    table_data = DataMeasurement.objects.all()
    psu1 = table_data.filter(psu = '01')
    context = { 'list': table_data, '1': psu1
                    }
    return render(request, 'table.html', context)
    """
    return table_page_view(request, 0)

@login_required
def table_page_view(request, page):
    return HttpResponse('You are currently on page {}.'.format(str(page)))
