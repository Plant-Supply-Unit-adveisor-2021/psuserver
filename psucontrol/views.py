from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import base64
from secrets import token_urlsafe, token_hex
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature

from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import timedelta, datetime

from psucontrol.models import PendingPSU, PSU, DataMeasurement

# Create your views here.

ERROR_CODES = {
    # A - Authentication
    '0xA1': 'Failed to identify PSU',
    '0xA2': 'Failed to authenticate PSU',
    # B - Bad request
    '0xB1': 'Bad request',
    # D - Database
    '0xD1': 'Failed to create new PSU',
    '0xD2': 'Failed to create new data measurement'
}


def remove_old_pending_psus():
    """
    will remove PendingPSUs which are older than one hour
    """
    for p in PendingPSU.objects.all():
        if timedelta(hours=1) < (timezone.now() - p.creation_time):
            p.delete()


def identify_psu(identity_key):
    """
    function to identify a PSU
    returns: corresponding PSU or None
    """
    try:
        return PSU.objects.get(identity_key=identity_key)
    except PSU.DoesNotExist:
        return None


def authenticate_psu(psu, message):
    """
    function to authenticate a psu
    returns: bool about access
    """
    try:
        # verify message
        public_key = serialization.load_pem_public_key(bytes(psu.public_rsa_key, 'utf-8'))
        public_key.verify(base64.urlsafe_b64decode(message), bytes(psu.current_challenge, 'utf-8'),
                          padding.PSS(
                              mgf=padding.MGF1(hashes.SHA256()),
                              salt_length=padding.PSS.MAX_LENGTH),
                          hashes.SHA256())
        # remove challenge
        psu.current_challenge = ""
        psu.save()
        return True
    except InvalidSignature:
        # remove challenge
        psu.current_challenge = ""
        psu.save()
        return False


def json_error_response(error_code):
    """
    queries ERROR_CODES to get error message
    returns: JsonRepsonse with status failed and error information
    """
    try:
        message = ERROR_CODES[error_code]
    except:
        message = 'Error Code ' + error_code
    return JsonResponse({'status': 'failed', 'error_code': error_code, 'error_message': message})


@csrf_exempt
@require_POST
def register_new_psu(request):
    """
    view to handle the first contact between psu and server
    """
    remove_old_pending_psus()

    if request.POST:
        # generate keys/tokens
        identity_key = token_urlsafe(96)
        pairing_key = token_hex(3).upper()

        # prevent non unique pairing Key
        while PendingPSU.objects.filter(pairing_key=pairing_key).count() != 0:
            pairing_key = token_hex(3).upper
        # prevent non unique identity key
        while PendingPSU.objects.filter(identity_key=identity_key).count() != 0 or PSU.objects.filter(
                identity_key=identity_key).count() != 0:
            identity_key = token_urlsafe(96)

        # try adding PendingPSU
        try:
            PendingPSU(identity_key=identity_key, pairing_key=pairing_key, public_rsa_key=request.POST['public_rsa_key']).save()
        except:
            # return creation error
            return json_error_response('0xD1')

        # successful request -> return identity_key and pairing_key
        return JsonResponse({'status': 'ok', 'identity_key': identity_key, 'pairing_key': pairing_key})
    else:
        # return bad request error
        return json_error_response('0xB1')


@csrf_exempt
@require_POST
def get_challenge(request):
    """
    view to handle the request of a new challenge
    expects the identity_key of the PSU
    """

    if request.POST:

        # identification of the PSU
        psu = identify_psu(request.POST['identity_key'])

        if psu is None:
            # return identification error
            return json_error_response('0xA1')

        # generate new challenge and store it
        challenge = token_urlsafe(96)
        psu.current_challenge = challenge
        psu.save()

        return JsonResponse({'status': 'ok', 'challenge': challenge})
    else:
        # return bad request type
        return json_error_response('0xB1')


@csrf_exempt
@require_POST
def add_data_measurement(request):
    """
    view to handle the process to add a new data entry
    """
    if request.POST:

        # identification of the PSU
        psu = identify_psu(request.POST['identity_key'])

        if psu is None:
            # return identification error
            return json_error_response('0xA1')

        # authenticate PSU
        if not authenticate_psu(psu, request.POST['signed_challenge']):
            # return authentication error
            return json_error_response('0xA2')

        # try to create new DataMeasurement
        try:
            DataMeasurement(psu=psu,
                            timestamp=make_aware(datetime.strptime(request.POST['timestamp'], '%Y-%m-%d_%H-%M-%S')),
                            temperature=float(request.POST['temperature']),
                            air_humidity=float(request.POST['air_humidity']),
                            ground_humidity=float(request.POST['ground_humidity']),
                            brightness=float(request.POST['brightness']),
                            fill_level=float(request.POST['fill_level'])).save()

        except Exception:
            # return creation error
            return json_error_response('0xD2')

        return JsonResponse({'status': 'ok'})
    else:
        # return bad request type
        return json_error_response('0xB1')
