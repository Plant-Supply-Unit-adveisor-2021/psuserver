from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm
from psucontrol.models import PSU, PendingPSU, DataMeasurement
from psucontrol.utils import get_psus_with_permission
from django.views.generic import ListView


# Create your views here.


class DataSet():
    """
    class holding pretty data for displaying it
    """
    def __init__(self, dm):
        """
        takes a DataMeasurement instance to generate pretty data
        """
        self.timestamp = dm.timestamp
        self.temperature = '{:.1f} °C'.format(dm.temperature)
        self.air_humidity = '{:.0f} %'.format(dm.air_humidity)
        self.ground_humidity = '{:.0f} %'.format(dm.ground_humidity)
        self.brightness = '{:.0f} %'.format(dm.brightness)
        self.fill_level = '{:.0f} %'.format(dm.fill_level)


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
     data_all = DataMeasurement.objects.all()

     paginator = Paginator(data_all, 30)

     page = request.GET.get('page')

     datas = paginator.get_page(page)

     return render(request, 'psufrontend/table.html', {'datas': datas})

@login_required
def table_filter(request, *, psu=0):
    # checking for which PSU the data should be displayed
    psus = get_psus_with_permission(request.user, 1)
    if len(psus) == 0:
        # display view later
        return None

    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    data_filter = DataMeasurement.objects.filter(psu=sel_psu)

    return render(request)

