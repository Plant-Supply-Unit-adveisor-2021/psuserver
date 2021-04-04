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
from django.utils.translation import gettext as _, gettext_noop
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from psucontrol.models import PendingPSU, PSU, DataMeasurement, CommunicationLogEntry

# Create your views here.

ERROR_CODES = {
    # A - Authentication
    '0xA1': gettext_noop('Failed to identify PSU'),
    '0xA2': gettext_noop('Failed to authenticate PSU'),
    '0xA3': gettext_noop('Failed to deserialize public key'),
    # B - Bad request
    '0xB1': gettext_noop('Bad request'),
    # D - Database
    '0xD1': gettext_noop('Failed to create new PSU'),
    '0xD2': gettext_noop('Failed to create new data measurement'),
    '0xD3': gettext_noop('Problems with making timestamp timezone aware.'),
    '0xD4': gettext_noop('The timestamp already exists for this PSU.'),
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


def respond_n_log(request, response, level, *, psu=None):
    """
    Adds a log entry and return JsonRepsonse
    returns: JsonResponse with the dict of response
    """
    #CommunicationLogEntry(psu=psu, request=str(request.POST), response=str(response), level=level, request_url=request.path).save()
    return JsonResponse(response)


def json_error_response(error_code):
    """
    queries ERROR_CODES to get error message
    returns: JsonResponse with status failed and error information
    """
    try:
        message = ERROR_CODES[error_code]
    except KeyError:
        message = 'Error Code ' + error_code

    context = {'status': 'failed', 'error_code': error_code, 'error_message': message}

    # translate messages
    for l in settings.LANGUAGES:
        translation.activate(l[0])
        context[ 'error_message_' + l[0] ] = _(context['error_message'])
        translation.deactivate()

    return context


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

            # prevent that another PSU has the same public_rsa_key
            if PSU.objects.filter(public_rsa_key=request.POST['public_rsa_key']).count() != 0:
                raise IntegrityError()

            # try to deserialize public key
            serialization.load_pem_public_key(bytes(request.POST['public_rsa_key'], 'utf-8'))
                
            # try adding PendingPSU
            PendingPSU(identity_key=identity_key, pairing_key=pairing_key,
                       public_rsa_key=request.POST['public_rsa_key']).save()
        
        except KeyError:
            # return bad request
            return respond_n_log(request, json_error_response('0xB1'), CommunicationLogEntry.Level.MAJOR_ERROR)

        except ValueError:
            # return 0xA3 as sign of wrong key format
            return respond_n_log(request, json_error_response('0xA3'), CommunicationLogEntry.Level.MAJOR_ERROR)

        except Exception as e:
            # return creation error
            return respond_n_log(request, json_error_response('0xD1'), CommunicationLogEntry.Level.ERROR)

        # successful request -> return identity_key and pairing_key
        return respond_n_log(request, {'status': 'ok', 'identity_key': identity_key, 'pairing_key': pairing_key}, CommunicationLogEntry.Level.MAJOR_INFO)
    else:
        # return bad request error
        return respond_n_log(request, json_error_response('0xB1'), CommunicationLogEntry.Level.MINOR_ERROR)


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
                return respond_n_log(request, json_error_response('0xA1'), CommunicationLogEntry.Level.ERROR)

            # generate new challenge and store it
            challenge = token_urlsafe(96)
            psu.current_challenge = challenge
            psu.save()

            return respond_n_log(request, {'status': 'ok', 'challenge': challenge}, CommunicationLogEntry.Level.MINOR_INFO)

        except KeyError:
            # return bad request
            return respond_n_log(request, json_error_response('0xB1'), CommunicationLogEntry.Level.MAJOR_ERROR)

    else:
        # return bad request type
        return respond_n_log(request, json_error_response('0xB1'), CommunicationLogEntry.Level.MINOR_ERROR)


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
                return respond_n_log(request, json_error_response('0xA1'), CommunicationLogEntry.Level.ERROR)

            # authenticate PSU
            if not authenticate_psu(psu, request.POST['signed_challenge']):
                # return authentication error
                return respond_n_log(request, json_error_response('0xA2'), CommunicationLogEntry.Level.ERROR)

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
            return respond_n_log(request, json_error_response('0xD3'), CommunicationLogEntry.Level.MAJOR_ERROR)
        except IntegrityError:
            # return already exists error
            return respond_n_log(request, json_error_response('0xD4'), CommunicationLogEntry.Level.MINOR_ERROR)
        except KeyError:
            # return bad request
            return respond_n_log(request, json_error_response('0xB1'), CommunicationLogEntry.Level.MAJOR_ERROR)
        except Exception:
            # return creation error
            return respond_n_log(request, json_error_response('0xD2'), CommunicationLogEntry.Level.ERROR)

        return respond_n_log(request, {'status': 'ok'}, CommunicationLogEntry.Level.MINOR_INFO)
    else:
        # return bad request type
        return respond_n_log(request, json_error_response('0xB1'), CommunicationLogEntry.Level.MINOR_ERROR)
