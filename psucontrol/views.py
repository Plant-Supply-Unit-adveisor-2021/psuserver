import base64
from datetime import timedelta, datetime
from pytz.exceptions import NonExistentTimeError
from secrets import token_urlsafe, token_hex

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from django.db.utils import IntegrityError
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone, translation
from django.utils.translation import gettext as _, gettext_noop as _noop
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from psucontrol.models import PendingPSU, PSU, DataMeasurement

# Create your views here.

ERROR_CODES = {
    # A - Authentication
    '0xA1': _noop('Failed to identify PSU'),
    '0xA2': _noop('Failed to authenticate PSU'),
    # B - Bad request
    '0xB1': _noop('Bad request'),
    # D - Database
    '0xD1': _noop('Failed to create new PSU'),
    '0xD2': _noop('Failed to create new data measurement'),
    '0xD3': _noop('Problems with making timestamp timezone aware.'),
    '0xD4': _noop('The timestamp already exists for this PSU.'),
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
    returns: JsonResponse with status failed and error information
    """
    try:
        message = ERROR_CODES[error_code]
    except:
        message = 'Error Code ' + error_code

    context = {'status': 'failed', 'error_code': error_code, 'error_message': message}

    # translate messages
    for l in settings.LANGUAGES:
        print(l)

    return JsonResponse({'status': 'failed', 'error_code': error_code, 'error_message': message})


@csrf_exempt
@require_POST
def register_new_psu(request):
    """
    view to handle the first contact between psu and server
    """
    remove_old_pending_psus()

    if request.POST:
        try:
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
            PendingPSU(identity_key=identity_key, pairing_key=pairing_key,
                       public_rsa_key=request.POST['public_rsa_key']).save()
        
        except KeyError:
            # return bad request
            return json_error_response('0xB1')

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
        
        try:
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

        except KeyError:
            # return bad request
            return json_error_response('0xB1')

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
        try:
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
            DataMeasurement(psu=psu,
                            timestamp=make_aware(datetime.strptime(request.POST['timestamp'], '%Y-%m-%d_%H-%M-%S')),
                            temperature=float(request.POST['temperature']),
                            air_humidity=float(request.POST['air_humidity']),
                            ground_humidity=float(request.POST['ground_humidity']),
                            brightness=float(request.POST['brightness']),
                            fill_level=float(request.POST['fill_level'])).save()

        except NonExistentTimeError:
            # return timezone error
            return json_error_response('0xD3')
        except IntegrityError:
            # return already exists error
            return json_error_response('0xD4')
        except KeyError:
            # return bad request
            return json_error_response('0xB1')
        except:
            # return creation error
            return json_error_response('0xD2')

        return JsonResponse({'status': 'ok'})
    else:
        # return bad request type
        return json_error_response('0xB1')
