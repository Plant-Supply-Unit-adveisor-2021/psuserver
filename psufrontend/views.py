from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm, AddWateringTaskForm, WateringControlForm, AddUserPermissionsForm, RevokeUserPermissionsForm
from psucontrol.models import CommunicationLogEntry, PSU, PSUImage, PendingPSU, DataMeasurement, WateringTask, WateringParams
from psucontrol.utils import get_psus_with_permission, get_users_with_permission, get_timedelta
from psucontrol.watering import CalculateWatering
from authentication.models import User

# Create your views here.

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


@csrf_exempt
@login_required
def change_user_permissions_view(request, psu=0):
    """
    view for changing user permissions for selected PSU
    """

    @csrf_protect
    def add_user_permission(request, form, psu):
        psu.permitted_users.add(form.cleaned_data['user'])
        psu.save()
        messages.success(request, _('Successfully added a new permitted user.'))

    @csrf_protect
    def revoke_user_permission(request, form, psu):
        psu.permitted_users.remove(form.cleaned_data['user'])
        psu.save()
        messages.success(request, _('Successfully revoked permission of {}.').format(form.cleaned_data['user'].pretty_name()))

    # gather the psus of the user with high priviledges
    psus = get_psus_with_permission(request.user, 10)
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    # Try finding the handed over PSU id in the list of psus
    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    context = {"psus": psus, "sel_psu": sel_psu}

    if request.POST and 'ADD' in request.POST:
        add_form = AddUserPermissionsForm(request.POST)
        if add_form.is_valid():
            # user clicked on add user
            add_user_permission(request, add_form, sel_psu)

    users = get_users_with_permission(sel_psu, min_level=1, max_level=9)

    if request.POST and 'REVOKE' in request.POST:
        revoke_form = RevokeUserPermissionsForm(users, request.POST)
        if revoke_form.is_valid():
            # user clicked on revoke permission
            revoke_user_permission(request, revoke_form, sel_psu)
            # reload users
            users = get_users_with_permission(sel_psu, min_level=1, max_level=9)

    context['users'] = users
    context['add_form'] = AddUserPermissionsForm()
    context['revoke_form'] = RevokeUserPermissionsForm(users)

    print(request.POST)

    return render(request, 'psufrontend/change_user_permissions.html', context=context)

    """
    # checking to which psus user has access
    psus = get_psus_with_permission(request.user, min_level=10)

    # checking for which PSU the permitted users should be displayed
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        users = None
    else:
        users = get_users_with_permission(sel_psu, min_level=1, max_level=11)

    form = ChangeUserPermissionsForm(request.POST or None)

    # redirection to other site
    if request.POST and form.is_valid():
        if sel_psu == None:
            if "1" in form.cleaned_data:
                return redirect('psufrontend:add_user_permissions')
            elif "2" in form.cleaned_data:
                return redirect('psufrontend:revoke_user_permissions')
        else:
            if "1" in form.cleaned_data:
                return redirect('psufrontend:add_user_permissions', psu=sel_psu.id)
            elif "2" in form.cleaned_data:
                return redirect('psufrontend:revoke_user_permissions', psu=sel_psu.id)

    return render(request, 'psufrontend/change_user_permissions.html',
                  context={'form': form, 'users': users, "psus": psus})
    """

def add_user_permissions_view(request, psu=0):
    # checking to which psus user has access
    psus = get_psus_with_permission(request.user, min_level=10)

    # checking for which PSU the permitted users should be displayed
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    users = get_users_with_permission(sel_psu, min_level=1, max_level=11)

    form = AddUserPermissionsForm(sel_psu, request.POST or None)

    if request.POST and form.is_valid():
        user = User.objects.get(email=form.cleaned_data)

        if user not in sel_psu.permitted_users.all():
            sel_psu.permitted_users.add(user)
            sel_psu.save()
            return redirect('psufrontend:add_user_permissions', psu=sel_psu.id)

    return render(request, 'psufrontend/add_user_permissions.html', context={'form': form, 'users': users, "psus": psus, "sel_psu": sel_psu})


def revoke_user_permissions_view(request, psu=0):
    # checking to which psus user has access
    psus = get_psus_with_permission(request.user, min_level=10)


    # checking for which PSU the permitted users should be displayed
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    sel_psu = None

    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    users = get_users_with_permission(sel_psu, min_level=1, max_level=11)

    form = RevokeUserPermissionsForm(users, request.POST or None)

    if request.POST and form.is_valid():
        user = User.objects.get(email=form.cleaned_data)

        if user in sel_psu.permitted_users.all():
            sel_psu.permitted_users.remove(user)
            sel_psu.save()
            return redirect('psufrontend:revoke_user_permissions', psu=sel_psu.id)

    return render(request, 'psufrontend/revoke_user_permissions.html',
                  context={'form': form, 'users': users, "psus": psus, "sel_psu": sel_psu})


@login_required
def table_view(request, *, psu=0):
    """
    view to present the DataMeasurements of one PSU in a tabular style to the user
    """

    # gather the psus of the user
    psus = get_psus_with_permission(request.user, 1)
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    # Try finding the handed over PSU id in the list of psus
    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    context = {"psus": psus, "sel_psu": sel_psu}

    # get measurements of the selected PSU
    measurements = DataMeasurement.objects.filter(psu=sel_psu)

    # catch case if there are no measurements
    if len(measurements) != 0:
        # set up paginator in order to create pages displaying the data
        paginator = Paginator(measurements, 30)
        measurements_on_page = paginator.get_page(request.GET.get('page'))

        context['measurements'] = measurements_on_page

    return render(request, 'psufrontend/table.html', context)


@login_required
def no_psu_view(request):
    """
    if a user does not have access to a PSU, he/she will be redirected to this page
    """
    return render(request, 'psufrontend/no_psu.html')


@csrf_exempt
@login_required
def add_watering_task_view(request, psu=0):
    """
    view for adding a watering task for a specific PSU
    """

    @csrf_protect
    def add_watering_task(request, form):
        # cancel old tasks
        for ot in WateringTask.objects.filter(psu=sel_psu, status__in=[0, 5]):
            ot.status = -10
            ot.save()
        # create WateringTask
        WateringTask.objects.create(psu=sel_psu, status=5, amount=form.cleaned_data['amount'])
        messages.success(request, _('Successfully added your watering request. It might take a few minutes to fullfill your request. Note: Only the lastest watering task will be fullfilled.'))
    
    # gather the psus of the user
    psus = get_psus_with_permission(request.user, 1)
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    # Try finding the handed over PSU id in the list of psus
    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]


    form = AddWateringTaskForm(request.POST or None)

    if request.POST and form.is_valid():
        add_watering_task(request, form)

    context = {"psus": psus, "sel_psu": sel_psu, "form": form}

    measurements = DataMeasurement.objects.filter(psu=sel_psu)
    context['measurement_count'] = len(measurements)
    if len(measurements) != 0:
        # hand over last 8 measurements to template
        context['measurements'] = measurements[:8]
        # get the last 8 wtaering tasks of a PSU 
        wateringtasks = WateringTask.objects.filter(psu=sel_psu)[:8]
        context['wateringtasks'] = wateringtasks

        if len(wateringtasks) != 0 and ( 0 < wateringtasks[0].status < 20 or (wateringtasks[0].status == 20 and wateringtasks[0].timestamp_execution - measurements[0].timestamp > timedelta())):
            context['old_data'] = True

    if not sel_psu.watering_params is None:
        context['alogrithm_amount'] = CalculateWatering(sel_psu).crunch_data_dry()
    else:
        context['alogrithm_amount'] = 0

    return render(request, 'psufrontend/add_watering_task.html', context=context)

@csrf_exempt    
@login_required
def watering_control_view(request, psu=0):
    """
    view for choosing a watering parameter and decide if one wants to water the PSU manually
    """

    # gather the psus of the user
    psus = get_psus_with_permission(request.user, 1)
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    # Try finding the handed over PSU id in the list of psus
    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    @csrf_protect
    def add_watering_control(request, form):
        sel_psu.watering_params = form.cleaned_data['watering_params']
        sel_psu.unauthorized_watering = form.cleaned_data['unauthorized_watering']
        sel_psu.save()
        messages.success(request, _('Successfully saved your watering settings.'))

    wateringparameters = WateringParams.objects.all()
    form = WateringControlForm(wateringparameters, sel_psu, request.POST or None)

    if request.POST and form.is_valid():
        add_watering_control(request, form)

    context = {"form": form, "psus": psus, "sel_psu": sel_psu}

    return render(request, 'psufrontend/watering_control.html', context)


@login_required
def dashboard_view(request, *, psu=0):
    """
    view for showing the newesst information to user
    """
    # gather the psus of the user
    psus = get_psus_with_permission(request.user, 1)
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    # Try finding the handed over PSU id in the list of psus
    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    context = {"psus": psus, "sel_psu": sel_psu}

    measurements = DataMeasurement.objects.filter(psu=sel_psu)
    context['measurement_count'] = len(measurements)
    if len(measurements) != 0:
        # hand over last 10 measurements to template
        context['measurements'] = measurements[:10]
        context['lastmeasurement'] = measurements[0]

        # get the last 5 wtaering tasks of a PSU 
        context['wateringtasks'] = WateringTask.objects.filter(psu=sel_psu)[:5]
        # get latest image of the PSU 
        context['lastimage'] = PSUImage.objects.filter(psu=sel_psu).first()

    # last communication log entry
    context['lastlog'] = CommunicationLogEntry.objects.filter(psu=sel_psu).exclude(request_uri='/psucontrol/get_challenge').first()

    return render(request, 'psufrontend/dashboard.html', context)


TIME_CHOICES = [
    (_('last 24h'), '1d'),
    (_('last 3 days'), '3d'),
    (_('last week'), '7d'),
    (_('last 2 weeks'), '14d'),
]


@login_required
def chart_view(request, *, psu=0, time_range=""):
    """
    view for chart
    """
    # gather the psus of the user
    psus = get_psus_with_permission(request.user, 1)
    if len(psus) == 0:
        # no psus -> redirect to the no_psu_view
        return redirect('psufrontend:no_psu')

    # Try finding the handed over PSU id in the list of psus
    sel_psu = None
    for p in psus:
        if p.id == psu:
            sel_psu = p
            break
    if sel_psu is None:
        # id not found -> take first psu in list
        sel_psu = psus[0]

    # Try to parse range to timedalta
    delta = get_timedelta(time_range)
    if delta is None:
        # go back to 3 days if there is no vaild range
        delta = timedelta(days=3)
        time_range = "3d"

    context = {"psus": psus, "sel_psu": sel_psu, "time_range": time_range, "time_choices": TIME_CHOICES}
    
    # get last measurment in order to display filllevel and take it as a reference point considering time
    lastmeasurement = DataMeasurement.objects.filter(psu=sel_psu).first()
    context['lastmeasurement'] = lastmeasurement

    if not lastmeasurement is None:
        # filter measurements of the last week from starting today
        start_time = lastmeasurement.timestamp - delta

        measurements = DataMeasurement.objects.filter(timestamp__gte = start_time, psu=sel_psu)
        context['measurements'] = measurements

    return render(request, 'psufrontend/chart.html', context=context)
