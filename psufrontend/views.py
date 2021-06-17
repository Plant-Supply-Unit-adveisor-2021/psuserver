from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator
from django.urls import resolve

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm, AddWateringTaskForm, ChangeUserPermissionsForm, AddUserPermissionsForm, \
    RevokeUserPermissionsForm
from psucontrol.models import PSU, PendingPSU, DataMeasurement, WateringTask
from psucontrol.utils import get_psus_with_permission, get_users_with_permission
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


@login_required
def change_user_permissions_view(request, psu=0):
    """
    view for changing user permissions for selected PSU
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
def add_watering_task_view(request):
    """
    view for adding a watering task for a specific PSU
    """

    @csrf_protect
    def add_watering_task(request, form):
        # cancel old tasks
        for ot in WateringTask.objects.filter(psu=form.cleaned_data['psu'], status__in=[0, 5]):
            ot.status = -10
            ot.save()
        # create WateringTask
        WateringTask.objects.create(psu=form.cleaned_data['psu'], status=5, amount=form.cleaned_data['amount'])
        messages.success(request,
                         _('Successfully added your watering request. It might take a few minutes to fullfill your request. Note: Only the lastest watering task will be fullfilled.'))

    psus = get_psus_with_permission(request.user, 1)
    form = AddWateringTaskForm(psus, request.POST or None)

    if request.POST and form.is_valid():
        add_watering_task(request, form)

    return render(request, 'psufrontend/add_watering_task.html', {'form': form})
