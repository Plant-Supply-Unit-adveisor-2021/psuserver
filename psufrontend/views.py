from django.shortcuts import render
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm, ChangeUserPermissionsForm
from psucontrol.models import PSU, PendingPSU, DataMeasurement
from psucontrol.utils import get_psus_with_permission, get_users_with_permission

# Create your views here.

ITEMS_PER_PAGE = 35


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
    def create_PSU(request, form):
        # get the corressponding PendingPSU
        pPSU = PendingPSU.objects.get(pairing_key=form.cleaned_data['pairing_key'])
        # create new PSU
        PSU(name=form.cleaned_data['name'], identity_key=pPSU.identity_key,
            public_rsa_key=pPSU.public_rsa_key, owner=request.user).save()
        # delete PendingPSU
        pPSU.delete()
        messages.success(request, _('Successfully registered your new Plant Supply Unit.'))

    form = RegisterPSUForm(request.POST or None)

    # check wether form was submitted correctly
    if request.POST and form.is_valid():
        create_PSU(request, form)

    return render(request, 'psufrontend/register_psu.html', {'form': form})


@login_required
def change_user_permissions_view(request, psu=0):
    """
    view for changing user permissions for selected PSU
    """

    # checking to which psus user has access
    psus = get_psus_with_permission(request.user, min_level=10)

    # checking for which PSU the permitted users should be displayed
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

    users = get_users_with_permission(sel_psu, min_level=1)

    form = ChangeUserPermissionsForm(psus, users, request.POST or None)

    return render(request, 'psufrontend/change_user_permissions.html', context={'form': form, "psus": psus, "sel_psu": sel_psu})


@login_required
def table_view(request, *, page=0, psu=0):
    """
    view to handle the tabular-style presentation of measurements
    """
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

    # gather data for sel_psu
    data_all = DataMeasurement.objects.filter(psu=sel_psu)
    data_count = len(data_all)

    # sorting out paging stuff
    max_page = int(data_count / ITEMS_PER_PAGE - 0.5)
    page = max(0, min(max_page, int(page)))
    # slice data according to page
    data_raw = data_all[(page * ITEMS_PER_PAGE): min(data_count, (page + 1) * ITEMS_PER_PAGE)]

    data = []
    for d in data_raw:
        data.append(DataSet(d))

    context = {
        'data': data,
    }

    return render(request, 'psufrontend/table.html', context=context)
