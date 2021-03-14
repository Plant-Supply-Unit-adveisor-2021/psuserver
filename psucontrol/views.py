from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from secrets import token_urlsafe, token_hex
from django.utils import timezone
from datetime import timedelta

from psucontrol.models import PendingPSU, PSU

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

    if request.POST:
        # generate keys/tokens
        iKey = token_urlsafe(96)
        pKey = token_hex(3).upper()

        # prevent non unique pairing Key
        while PendingPSU.objects.filter(pairing_key=pKey).count() != 0:
            pKey = token_hex(3).upper
        # prevent non unique identity key
        while PendingPSU.objects.filter(identity_key=iKey).count() != 0 or PSU.objects.filter(identity_key=iKey).count() != 0:
            iKey = token_urlsafe(96)

        # try adding PendingPSU
        try:
            PendingPSU(identity_key=iKey, pairing_key=pKey, public_rsa_key=request.POST['public_rsa_key']).save()
        except:
            print('PROBLEM')
            return JsonResponse({'status':'failed'})

        # successful request -> return iKey and pKey
        return JsonResponse({'status':'ok', 'identity_key':iKey, 'pairing_key':pKey})
    else:
        return JsonResponse({'status':'failed'})
