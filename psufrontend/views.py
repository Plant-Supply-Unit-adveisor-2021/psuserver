from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator

from django.utils import timezone
from datetime import timedelta
import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm, AddWateringTaskForm
from psucontrol.models import PSU, PendingPSU, DataMeasurement,WateringTask
from psucontrol.utils import get_psus_with_permission


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
        create_psu(request, form)
    
    return render(request, 'psufrontend/register_psu.html', {'form':form})

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
        messages.success(request, _('Successfully added your watering request. It might take a few minutes to fullfill your request. Note: Only the lastest watering task will be fullfilled.'))
    
    psus = get_psus_with_permission(request.user, 1)
    form = AddWateringTaskForm(psus, request.POST or None)

    if request.POST and form.is_valid():
        add_watering_task(request, form)

    return render(request, 'psufrontend/add_watering_task.html', {'form': form})


@login_required
def chart_view(request, *, psu=0, day=0):
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

    context = {"psus": psus, "sel_psu": sel_psu}

    c_measurements = DataMeasurement.objects.filter(psu=sel_psu)


    
    # catch case if there are no measurements
    if len(c_measurements) != 0:
        # set up paginator in order to create pages displaying the data
        paginator = Paginator(c_measurements, 30)
        c_measurements_on_page = paginator.get_page(request.GET.get('page'))

        context['c_measurements'] = c_measurements_on_page

    # get measurements of the selected PSU
    measurements = DataMeasurement.objects.filter(psu=sel_psu).first()
    
    #get last measurment for filllevel diagramm

    lastmeasurement = DataMeasurement.objects.filter(psu=sel_psu).first()
    context['lastmeasurement'] = lastmeasurement

    #filter measurements of the last week from starting today

    week = lastmeasurement.timestamp - timedelta(days=7)

    week_measurements = DataMeasurement.objects.filter(timestamp__gte = week, psu=sel_psu)
    context['week_measurements'] = week_measurements 

    # measurements for one day starting with yesterday
    day1 = lastmeasurement.timestamp - timedelta(days=1)
    day2 = lastmeasurement.timestamp - timedelta(days=2)
    day3 = lastmeasurement.timestamp - timedelta(days=3)

    today = DataMeasurement.objects.filter(timestamp__gte = day1, psu=sel_psu)
    context['today']=today

    day1_ago = DataMeasurement.objects.filter(timestamp__range=(day2, day1), psu=sel_psu) 
    context['day1_ago'] = day1_ago

    day2_ago = DataMeasurement.objects.filter(timestamp__range=(day3, day2), psu=sel_psu) 
    context['day2_ago'] = day2_ago

    days = [today, day1_ago, day2_ago, week_measurements]

    sel_day = None
    for choice in days:
        if choice == day:
            sel_day = choice
            break
    if sel_day is None:
        # id not found -> take first psu in list
        sel_day= days[0]

    context = {"days": days, "sel_day": sel_day}

    return render(request, 'psufrontend/chart.html', context=context)
