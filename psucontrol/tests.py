from django.test import TestCase, Client, TransactionTestCase
from django.db import transaction
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

from website.utils import get_test_user
from psucontrol.models import PSU, PendingPSU, DataMeasurement, CommunicationLogEntry

# Create your tests here.


class PSUCommunicationTestCase(TransactionTestCase):
    """
    TestCase to test the whole communication between a psu and django
    """

    def setUp(self):
        """
        setup of the testing environment
        """
        # create new private rsa key
        self.rsa_pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pub_rsa_str = str(self.rsa_pk.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo), 'utf-8')
        self.psu = PSU.objects.create(name='TEST-PSU', identity_key='test-key', public_rsa_key=pub_rsa_str, owner=get_test_user())
    

    def get_signed_msg(self,* ,client=None):
        """
        function to request a chellenge and sign it with the key of self.psu
        """
        if client is None:
            client = Client()

        uri = '/psucontrol/get_challenge'
        data = {'identity_key': self.psu.identity_key}
        res = self.check_status(uri, True, data=data, client=client)
        # test returned challenge
        try:
            self.failUnlessEqual(len(res['challenge']), 128, self.gen_fmsg(uri, data, res, '128 char challenge'))
        except KeyError:
            self.fail(self.gen_fmsg(uri, data, res, 'challenge (KeyError)'))
        
        signed = self.rsa_pk.sign(bytes(res['challenge'], 'utf-8'),
                                  padding.PSS(
                                      mgf=padding.MGF1(hashes.SHA256()),
                                      salt_length=padding.PSS.MAX_LENGTH),
                                  hashes.SHA256())
        # return url safe string
        return str(base64.urlsafe_b64encode(signed), 'utf-8')
    
    
    def gen_fmsg(self, uri, data, res, wanted_str):
        """
        shortcut to create error message
        """
        return 'Requested {} with {} and got {} but wanted {}.'.format(uri, str(data), str(res), wanted_str)


    def check_dict_value(self, uri, data, res, key, wanted):
        """
        shortcut to check the value of a dict and throw an error if res[key] != wanted
        """
        if data is None:
            data = dict()

        try:
            self.failUnlessEqual(res[key], wanted, self.gen_fmsg(uri, data, res, '{}: {}'.format(key, wanted)))
        except KeyError:
            self.fail(self.gen_fmsg(uri, data, res, '{}: {} (KeyError).'.format(key, wanted)))


    def check_status(self, uri, ok, *, data=None, client=None):
        """
        make post request and test whether the correct status was reported
        addtionally test wehter the log entry was added correctly
        returns the JSON of the response
        """
        if client is None:
            client = Client()
        if data is None:
            data = dict()

        # make post request
        res = client.post(uri, data=data).json()

        # check log entry
        entry = CommunicationLogEntry.objects.first()
        # test existance
        if entry is None:
            self.fail('No log entry was added for request {} and response {}'.format(str(data), str(res)))
        else:
            # test three major values
            self.failUnlessEqual(entry.request, str(data), 'last log entry holds request {} but {} was requested'.format(entry.request, str(data)))
            self.failUnlessEqual(entry.request_uri, uri, 'last log entry holds request_uri {} but {} was requested'.format(entry.request_uri, uri))
            self.failUnlessEqual(entry.response, str(res), 'last log entry holds response {} but {} was received'.format(entry.response, str(res)))

        # check status
        if ok:
            self.check_dict_value(uri, data, res, 'status', 'ok')
        else:
            self.check_dict_value(uri, data, res, 'status', 'failed')

        return res


    def check_error_code(self, uri, error_code, *, data=None, client=None):
        """
        make post request and test whether the corresponding error_code was responded
        """
        # check status failed
        res = self.check_status(uri, False, data=data, client=client)
        # check error code
        self.check_dict_value(uri, data, res, 'error_code', error_code)


    def test_registration(self):
        """
        test the registration process
        """
        uri = '/psucontrol/register_new_psu'

        c = Client()

        # Test error 0xB1 if no post data is given
        self.check_error_code(uri, '0xB1', client=c)

        # Test error 0xB1 if wrong post data is given
        self.check_error_code(uri, '0xB1', data={'test':'test'}, client=c)

        # Test wrong public_rsa_key format
        self.check_error_code(uri, '0xA3', data={'public_rsa_key': 'TESTING KEY'}, client=c)

        # Test registration of PSU with non unique public_rsa_key
        pub_rsa_str = str(self.rsa_pk.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo), 'utf-8')
        data = {'public_rsa_key': pub_rsa_str}
        self.check_error_code(uri, '0xD1', data=data, client=c)

        # Test registration process
        pub_rsa_str = str(rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo), 'utf-8')
        data = {'public_rsa_key': pub_rsa_str}
        res = self.check_status(uri, True, data=data, client=c)

        # check returned keys
        try:
            self.failUnlessEqual(len(res['identity_key']), 128, self.gen_fmsg(uri, data, res, '128 char identity_key'))
            self.failUnlessEqual(len(res['pairing_key']), 6, self.gen_fmsg(uri, data, res, '6 char pairing_key'))
            self.iKey = res['identity_key']
        except KeyError:
            self.fail(self.gen_fmsg(uri, data, res, 'identity_key and pairing_key (KeyError)'))

        # check wether PendingPSU was created
        try:
            PendingPSU.objects.get(identity_key=self.iKey)
        except PendingPSU.DoesNotExist:
            self.fail(self.gen_fmsg(uri, data, res, 'server to create PendingPSU'))

        # Test registration of PSU with non unique public_rsa_key (PendingPSU)
        self.check_error_code(uri, '0xD1', data=data, client=c)


    def test_get_challenge(self):
        """
        test process of getting a challenge from the server
        """
        uri = '/psucontrol/get_challenge'
        data = {'identity_key': self.psu.identity_key}

        c = Client()

        # Test error 0xB1 if no post data is given
        self.check_error_code(uri, '0xB1', client=c)

        # Test error 0xB1 if wrong post data is given
        self.check_error_code(uri, '0xB1', data={'test':'test'}, client=c)

        # Test error 0xA1 if wrong identity_key is given
        self.check_error_code(uri, '0xA1', data={'identity_key':'somekey'}, client=c)

        # Test to really get a challenge
        res = self.check_status(uri, True, data=data, client=c)
        # test returned challenge
        try:
            self.failUnlessEqual(len(res['challenge']), 128, self.gen_fmsg(uri, data, res, '128 char challenge'))
        except KeyError:
            self.fail(self.gen_fmsg(uri, data, res, 'challenge (KeyError)'))
        # test if challenge was stored
        self.psu.refresh_from_db()
        self.failUnlessEqual(self.psu.current_challenge, res['challenge'], 'psu holds current challenge {} but {} was responeded'.format(self.psu.current_challenge, res['challenge']))


    def test_add_data_measurement(self):
        """
        test process of adding a data measurement
        """
        uri = '/psucontrol/add_data_measurement'

        c = Client()

        # Test error 0xB1 if no post data is given
        self.check_error_code(uri, '0xB1', client=c)

        # Test error 0xB1 if wrong post data is given
        self.check_error_code(uri, '0xB1', data={'test':'test'}, client=c)

        # Test error 0xA1 if wrong identity_key is given
        self.check_error_code(uri, '0xA1', data={'identity_key':'somekey'}, client=c)

        # Test error 0xA2 if wrong signed challenge is given
        data = {'identity_key':self.psu.identity_key, 'signed_challenge': 'some weird challenge'}
        self.check_error_code(uri, '0xA2', data=data, client=c)

        # Test error 0xB1 if wrong post data except auth stuff is given
        data['signed_challenge'] = self.get_signed_msg()
        self.check_error_code(uri, '0xB1', data=data, client=c)
        
        data['temperature'] = '20.0'
        data['air_humidity'] = '98.9'
        data['ground_humidity'] = '45.65'
        data['brightness'] = '100.0'
        data['fill_level'] = '75.6'

        # Test error 0xD3 if there is a timestamp parsing problem
        data['signed_challenge'] = self.get_signed_msg()
        data['timestamp'] = '2021-03-28_02:30:25'
        self.check_error_code(uri, '0xD3', data=data, client=c)

        # Test error 0xD3 if there is a timezone problem
        data['signed_challenge'] = self.get_signed_msg()
        data['timestamp'] = '2021-03-28_02-30-25'
        self.check_error_code(uri, '0xD3', data=data, client=c)

        # Test creating a DataMeasurement
        data['signed_challenge'] = self.get_signed_msg()
        data['timestamp'] = '2021-03-28_03-30-25'
        res = self.check_status(uri, True, data=data, client=c)
        
        # Test whether correct DataMeasurement was created
        dm = DataMeasurement.objects.first()
        if dm is None:
            self.fail('No DataMeasurement was added for request {} and response {}'.format(str(data), str(res)))
        else:
            # test every attribute
            self.psu.refresh_from_db()
            self.failUnlessEqual(dm.psu, self.psu, 'DataMeasurement holds psu {} but {} was requested'.format(str(dm.psu), str(self.psu)))
            self.failUnlessEqual(dm.timestamp.strftime('%Y-%m-%d_%H-%M-%S'), '2021-03-28_01-30-25', 'DataMeasurement holds psu {} but {} was requested'.format(dm.timestamp.strftime('%Y-%m-%d_%H-%M-%S'), '2021-03-28_01-30-25'))
            self.failUnlessEqual(dm.temperature, 20.0, 'DataMeasurement holds temperature {} but {} was requested'.format(str(dm.temperature), str(20.0)))
            self.failUnlessEqual(dm.air_humidity, 98.9, 'DataMeasurement holds air_humidity {} but {} was requested'.format(str(dm.air_humidity), str(98.8)))
            self.failUnlessEqual(dm.ground_humidity, 45.65, 'DataMeasurement holds ground_humidity {} but {} was requested'.format(str(dm.ground_humidity), str(46.65)))
            self.failUnlessEqual(dm.brightness, 100.0, 'DataMeasurement holds brightness {} but {} was requested'.format(str(dm.brightness), str(100.0)))
            self.failUnlessEqual(dm.fill_level, 75.6, 'DataMeasurement holds fill_level {} but {} was requested'.format(str(dm.fill_level), str(75.6)))

        # Test error 0xA2 after direct resend without new signed_challenge
        self.check_error_code(uri, '0xA2', data=data, client=c)

        # Test error 0xA2 when using no message as message
        signed = self.rsa_pk.sign(bytes('', 'utf-8'),
                                  padding.PSS(
                                      mgf=padding.MGF1(hashes.SHA256()),
                                      salt_length=padding.PSS.MAX_LENGTH),
                                  hashes.SHA256())
        data['signed_challenge'] = str(base64.urlsafe_b64encode(signed), 'utf-8')
        self.check_error_code(uri, '0xA2', data=data, client=c)

        # Test 0xD4 if measurement already exists
        data['signed_challenge'] = self.get_signed_msg()
        self.check_error_code(uri, '0xD4', data=data, client=c)
