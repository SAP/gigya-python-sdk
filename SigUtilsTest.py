import unittest
import time
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from GSSDK import SigUtils

class TestSigUtils(unittest.TestCase):

    @patch('GSSDK.SigUtils.validateUserSignature')
    def test_validate_user_signature_with_expiration_use_expired_timestamp(self, mock_validateUserSignature):
        mock_validateUserSignature.rreturn_value = True
        UIDtimestamp = "1586977937"
        
        valid = SigUtils.validateUserSignatureWithExpiration("UID", UIDtimestamp, "secret", "signature", 180)
        self.assertFalse(valid)

    @patch('GSSDK.SigUtils.validateUserSignature')
    def test_validate_user_signature_with_expiration_use_valid_timestamp(self, mock_validateUserSignature):
        mock_validateUserSignature.rreturn_value = True
        now = int(round(time.time()) + 60)
        UIDtimestamp = str(now)

        valid = SigUtils.validateUserSignatureWithExpiration("UID", UIDtimestamp, "secret", "signature", 180)
        self.assertTrue(valid)

if __name__ == '__main__':
    unittest.main()