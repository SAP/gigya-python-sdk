import unittest
from GSSDK import GSRequest


class TestResolveMtlsDomain(unittest.TestCase):

    def _make_request(self, api_domain=None):
        request = GSRequest(
            apiKey="test_key",
            secretKey="test_secret",
            apiMethod="accounts.getAccountInfo",
            useHTTPS=True,
            certFile="cert.pem",
            keyFile="key.pem"
        )
        if api_domain:
            request.setAPIDomain(api_domain)
        return request

    def test_default_domain(self):
        request = self._make_request()
        self.assertEqual(request._resolve_mtls_domain(), "mtls.us1.gigya.com")

    def test_us1(self):
        request = self._make_request("us1.gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.us1.gigya.com")

    def test_eu1(self):
        request = self._make_request("eu1.gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.eu1.gigya.com")

    def test_eu2(self):
        request = self._make_request("eu2.gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.eu2.gigya.com")

    def test_au1(self):
        request = self._make_request("au1.gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.au1.gigya.com")

    def test_global(self):
        request = self._make_request("global.gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.global.gigya.com")

    def test_staging_domain(self):
        request = self._make_request("us1-st1.gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.us1-st1.gigya.com")

    def test_empty_string_resets_to_default(self):
        """setAPIDomain('') resets to default us1.gigya.com, so resolves to mtls.us1.gigya.com"""
        request = self._make_request()
        request.setAPIDomain("")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.us1.gigya.com")

    def test_bare_domain(self):
        """bare domain (gigya.com) - first segment is gigya, so resolves to mtls.gigya.gigya.com"""
        request = self._make_request("gigya.com")
        self.assertEqual(request._resolve_mtls_domain(), "mtls.gigya.gigya.com")

    def test_leading_dot(self):
        """leading dot (.gigya.com) - first segment is empty, fallback kicks in"""
        request = self._make_request()
        request._apiDomain = ".gigya.com"
        self.assertEqual(request._resolve_mtls_domain(), "mtls.us1.gigya.com")


class TestHasMtlsConfig(unittest.TestCase):

    def test_both_provided(self):
        request = GSRequest(
            apiKey=None, secretKey=None, apiMethod="accounts.getAccountInfo",
            useHTTPS=True, certFile="cert.pem", keyFile="key.pem"
        )
        self.assertTrue(request._has_mtls_config())

    def test_no_cert(self):
        request = GSRequest(
            apiKey="key", secretKey="secret", apiMethod="accounts.getAccountInfo",
            useHTTPS=True, certFile=None, keyFile=None
        )
        self.assertFalse(request._has_mtls_config())

    def test_only_cert_no_key(self):
        request = GSRequest(
            apiKey=None, secretKey=None, apiMethod="accounts.getAccountInfo",
            useHTTPS=True, certFile="cert.pem", keyFile=None
        )
        self.assertFalse(request._has_mtls_config())

    def test_only_key_no_cert(self):
        request = GSRequest(
            apiKey=None, secretKey=None, apiMethod="accounts.getAccountInfo",
            useHTTPS=True, certFile=None, keyFile="key.pem"
        )
        self.assertFalse(request._has_mtls_config())


class TestSendDomainResolution(unittest.TestCase):
    """Test that send() sets _domain correctly for mTLS vs regular requests"""

    def test_mtls_overrides_domain(self):
        request = GSRequest(
            apiKey=None, secretKey=None, apiMethod="accounts.getAccountInfo",
            useHTTPS=True, certFile="cert.pem", keyFile="key.pem"
        )
        request.setAPIDomain("eu1.gigya.com")
        # Call send — it will fail on the actual HTTP call, but domain is set before that
        request.send(timeout=1)
        self.assertEqual(request._domain, "mtls.eu1.gigya.com")

    def test_regular_request_uses_namespace_domain(self):
        request = GSRequest(
            apiKey="key", secretKey="secret", apiMethod="accounts.getAccountInfo",
            useHTTPS=True
        )
        request.setAPIDomain("eu1.gigya.com")
        request.send(timeout=1)
        self.assertEqual(request._domain, "accounts.eu1.gigya.com")


if __name__ == '__main__':
    unittest.main()
