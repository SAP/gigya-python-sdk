# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
# Import modules for CGI handling
import cgi, cgitb

cgitb.enable()
# from json import loads as jsonparse
from GSSDK import *

testUrlOpener = False

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
apiKey = form.getvalue('apiKey')
secret = form.getvalue('secret')
method = form.getvalue('method')
params = form.getvalue('params')

useHttps = form.getvalue('useHttps') == "1" or form.getvalue('useHttps') == "true"
userKey = form.getvalue('userKey')
apiDomain = form.getvalue('apiDomain')
timeout = form.getvalue('timeout')

printHtml = form.getvalue('printHtml')
if printHtml is None:
    printHtml = False

if printHtml:
    print("HTTP/1.0 200 OK\n")
    print("Content-Type: text/html\n\n\n")

if testUrlOpener:
    req = urlopen("http://en.wikipedia.org/wiki/Python_(programming_language)")
    print(req.read())
    install_opener(build_opener())
    req = urlopen("https://example.com")
    print(req.read())

req = GSRequest(apiKey, secret, method, params, useHttps, userKey)
req.setAPIDomain(apiDomain)

if timeout != None:
    res = req.send(timeout)
else:
    res = req.send()

print('x-proxy-log:' + res.getLog().replace("\r\n", " "))

if printHtml:
    print("<h1>response</h1>")
    print("<textarea style='width:100%;height:300px'>")
    print(res.getResponseText())
    print("</textarea>")
    print("<h1>Log</h1>")
    print("<textarea style='width:100%;height:500px'>")
    print(res.getLog())
    print("</textarea>")
else:
    print(res.getResponseText())

if testUrlOpener:
    # HTTPS will fail if GSRequest didn't restore the urllib's opener
    req = urlopen("https://example.com")
    print(req.read())
