from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import base64
from secrets import token_urlsafe, token_hex
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
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

def check_challenge_response(identity_key, response):
    """
    function to check wether challenge-response-authentifiction was successful
    return None or the corresponding PSU
    """
    print(response)
    try:
        psu = PSU.objects.get(identity_key=identity_key)
    except:
        return None
    
    try:
        public_key = serialization.load_pem_public_key(bytes(psu.public_rsa_key, 'utf-8'))
        public_key.verify(base64.urlsafe_b64decode(response), psu.current_challenge,
                          padding.PSS(
                              mgf=padding.MGF1(hashes.SHA256()),
                              salt_length=padding.PSS.MAX_LENGTH),
                          hashes.SHA256())
        psu.current_challenge = ""
        psu.save()
        return psu
    except:
        psu.current_challenge = ""
        psu.save()
        return None
    

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
            return JsonResponse({'status':'failed'})

        # successful request -> return iKey and pKey
        return JsonResponse({'status':'ok', 'identity_key':iKey, 'pairing_key':pKey})
    else:
        return JsonResponse({'status':'failed'})

@csrf_exempt
@require_POST
def get_challenge(request):
    """
    view to handle the request of a new challenge
    expects the identity_key of the PSU
    """

    if request.POST:
        # generate new challenge
        challenge = token_urlsafe(96)
        try:
            psu = PSU.objects.get(identity_key=request.POST['identity_key'])
            psu.current_challenge = challenge
            psu.save()
        except:
            return JsonResponse({'status':'failed'})
        
        return JsonResponse({'status':'ok','challenge':challenge})
    else:
        return JsonResponse({'status':'failed'})
