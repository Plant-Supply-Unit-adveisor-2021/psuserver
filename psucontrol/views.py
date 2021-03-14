from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from secrets import token_urlsafe
from django.utils import timezone
from datetime import timedelta

from psucontrol.models import PendingPSU

# Create your views here.

def remove_old_pending_psus():
    """
    will remove PendingPSUs which are older than one hour
    """
    for p in PendingPSU.objects.all():
        if timedelta(hours=1) < (timezone.now() - p.creation_time):
            p.delete()

@csrf_exempt
@require_POST
def register_new_psu(request):
    """
    view to handle the first contact between psu and server
    """
    remove_old_pending_psus()

    # generate keys/tokens
    iKey = token_urlsafe(96)
    pKey = token_urlsafe(4)
    # prevent pairing key with '_', '-'
    while pKey.count('_') != 0 or pKey.count('-') != 0:
        pKey = token_urlsafe(4)
    PendingPSU(identity_key=iKey, pairing_key=pKey).save()
    return JsonResponse({'status':'ok', 'identity_key':iKey, 'pairing_key':pKey})
