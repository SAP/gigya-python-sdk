import unittest
import time

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from GSSDK import SigUtils


class TestSigUtils(unittest.TestCase):

    @patch('GSSDK.SigUtils.calcSignature')
    def test_validate_user_signature_use_expired_timestamp(self, mock_calc_signature):
        mock_calc_signature.return_value = "signature"
        uid_timestamp = "1586977937"

        valid = SigUtils.validateUserSignature("UID", uid_timestamp, "secret", "signature", 180)
        self.assertFalse(valid)

    @patch('GSSDK.SigUtils.calcSignature')
    def test_validate_user_signature_use_valid_timestamp(self, mock_calc_signature):
        mock_calc_signature.return_value = "signature"
        now = int(round(time.time()) + 80)
        uid_timestamp = str(now)

        valid = SigUtils.validateUserSignature("UID", uid_timestamp, "secret", "signature", 180)
        self.assertTrue(valid)

    @patch('GSSDK.SigUtils.calcSignature')
    def test_validate_user_signature_with_default_expiration_value(self, mock_calc_signature):
        mock_calc_signature.return_value = "signature"
        uid_timestamp = "1586977937"

        valid = SigUtils.validateUserSignature("UID", uid_timestamp, "secret", "signature")
        self.assertTrue(valid)

    @patch('GSSDK.SigUtils.validateUserSignature')
    def test_validate_user_signature_with_expiration_use_expired_timestamp(self, mock_validate_user_signature):
        mock_validate_user_signature.return_value = True
        uid_timestamp = "1586977937"

        valid = SigUtils.validateUserSignatureWithExpiration("UID", uid_timestamp, "secret", "signature", 180)
        self.assertFalse(valid)

    @patch('GSSDK.SigUtils.validateUserSignature')
    def test_validate_user_signature_with_expiration_use_valid_timestamp(self, mock_validate_user_signature):
        mock_validate_user_signature.return_value = True
        now = int(round(time.time()) + 60)
        uid_timestamp = str(now)

        valid = SigUtils.validateUserSignatureWithExpiration("UID", uid_timestamp, "secret", "signature", 180)
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
