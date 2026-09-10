import unittest
import ssl
import socket
from unittest.mock import MagicMock, patch
from GSSDK import GSRequest, ValidHTTPSConnection, SSLUtils


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


class TestValidHTTPSConnectionSNI(unittest.TestCase):
    """
    Tests for the SNI fix in ValidHTTPSConnection.connect().

    When routing through an HTTPS proxy (CONNECT tunnel), urllib sets:
      self.host         = proxy address
      self._tunnel_host = real destination hostname

    The fix ensures the real destination is used as SNI, not the proxy.
    """

    def _make_connection(self, host, tunnel_host=None):
        ctx = SSLUtils.createSSLContext(False, None, None)
        conn = ValidHTTPSConnection(host, context=ctx)
        conn._tunnel_host = tunnel_host
        conn.timeout = 5
        conn.source_address = None
        return conn

    def _mock_socket(self):
        sock = MagicMock()
        sock.setsockopt = MagicMock()
        return sock

    def test_sni_uses_tunnel_host_when_proxy_is_set(self):
        """When going through a proxy, SNI must be the destination host, not the proxy."""
        conn = self._make_connection("127.0.0.1", tunnel_host="accounts.us1.gigya.com")
        mock_sock = self._mock_socket()
        captured_sni = []

        def fake_wrap(sock, server_hostname=None):
            captured_sni.append(server_hostname)
            raise ConnectionAbortedError("stop after SNI capture")

        conn._context.wrap_socket = fake_wrap

        with patch("socket.create_connection", return_value=mock_sock):
            with patch.object(conn, "_tunnel"):
                try:
                    conn.connect()
                except ConnectionAbortedError:
                    pass

        self.assertEqual(captured_sni, ["accounts.us1.gigya.com"],
            "SNI must be the tunnel destination, not the proxy address")

    def test_sni_uses_host_when_no_proxy(self):
        """Without a proxy, SNI must be self.host (direct connection, no tunnel)."""
        conn = self._make_connection("accounts.us1.gigya.com", tunnel_host=None)
        mock_sock = self._mock_socket()
        captured_sni = []

        def fake_wrap(sock, server_hostname=None):
            captured_sni.append(server_hostname)
            raise ConnectionAbortedError("stop after SNI capture")

        conn._context.wrap_socket = fake_wrap

        with patch("socket.create_connection", return_value=mock_sock):
            try:
                conn.connect()
            except ConnectionAbortedError:
                pass

        self.assertEqual(captured_sni, ["accounts.us1.gigya.com"],
            "SNI must be self.host for direct connections")

    def test_sni_not_proxy_ip(self):
        """Regression: the proxy IP must never appear as SNI."""
        conn = self._make_connection("10.0.0.1", tunnel_host="accounts.eu1.gigya.com")
        mock_sock = self._mock_socket()
        captured_sni = []

        def fake_wrap(sock, server_hostname=None):
            captured_sni.append(server_hostname)
            raise ConnectionAbortedError("stop after SNI capture")

        conn._context.wrap_socket = fake_wrap

        with patch("socket.create_connection", return_value=mock_sock):
            with patch.object(conn, "_tunnel"):
                try:
                    conn.connect()
                except ConnectionAbortedError:
                    pass

        self.assertNotEqual(captured_sni[0], "10.0.0.1",
            "Proxy IP must never be sent as SNI")
        self.assertEqual(captured_sni[0], "accounts.eu1.gigya.com",
            "SNI must be the real destination hostname")


if __name__ == '__main__':
    unittest.main()
