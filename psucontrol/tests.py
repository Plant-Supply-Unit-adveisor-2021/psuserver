from django.test import TestCase, Client
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Create your tests here.


class PSUCommunicationTestCase(TestCase):
    """
    TestCase to test the whole communication between a psu and django
    """

    def setUp(self):
        """
        setup of the testing environment
        """
        # create new private rsa key
        self.rsa_pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    

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
        returns the JSON of the response
        """
        if client is None:
            client = Client()
        if data is None:
            data = dict()

        res = client.post(uri, data=data).json()
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
        # self.check_error_code(uri, '0xA3', data={'public_rsa_key': 'TESTING KEY'}, client=c)

        # Test registration of PSU with non unique public_rsa_key
        pub_rsa_str = str(self.rsa_pk.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo), 'utf-8')
        data = {'public_rsa_key': pub_rsa_str}
        # self.check_error_code(uri, '0xD1', data=data, client=c)

        # Test registration process
        pub_rsa_str = str(rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo), 'utf-8')
        data ={'public_rsa_key': pub_rsa_str}
        res = self.check_status(uri, True, data=data, client=c)

        # check returned keys
        try:
            if len(res['identity_key']) != 128:
                self.fail(self.gen_fmsg(uri, data, res, '128 char identity_key'))
            if len(res['pairing_key']) != 6:
                self.fail(self.gen_fmsg(uri, data, res, '6 char pairing_key'))
            self.iKey = res['identity_key']
        except KeyError:
            self.fail(self.gen_fmsg(uri, data, res, 'identity_key and pairing_key (KeyError).'))

        # Test registration of PSU with non unique public_rsa_key (PendingPSU)
        self.check_error_code(uri, '0xD1', data=data, client=c)
