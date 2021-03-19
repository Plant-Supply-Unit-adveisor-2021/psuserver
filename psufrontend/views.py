from django.shortcuts import render
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from psufrontend.forms import RegisterPSUForm
from psucontrol.models import PSU, PendingPSU

# Create your views here.

@csrf_exempt
@login_required
def register_psu_view(request):
    """
    view for setting up a new psu and converting a PendingPSU in a PSU
    """
    
    @csrf_protect
    def create_PSU(request, form):
        pass

    form = RegisterPSUForm(request.POST or None)

    if request.POST:
        create_PSU(request, form)
    
    return render(request, 'psufrontend/register_psu.html', {'form':form})
