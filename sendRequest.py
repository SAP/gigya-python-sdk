# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
# Import modules for CGI handling
import cgi, cgitb

cgitb.enable()
# from json import loads as jsonparse
from GSSDK import *


# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get data from fields
apiKey = form.getvalue('apiKey')
debug = form.getvalue('debug')
if (debug == None):
    debug = 0
secret = form.getvalue('secret')
method = form.getvalue('method')

#params = form.getvalue('params')

params = {
	"UID": "_guid_e4WvAOTp8xsl8jmh2lbPHg==",
	"categoryID": "comments1",
	"streamID": "~#$%&'()*+,-./:;<=>?_«aZ09»",
	"commentText": "«utf8-str2»"
}

useHttps = form.getvalue('useHttps') == "1" or form.getvalue('useHttps') == "true"
userKey = form.getvalue('userKey')
apiDomain = form.getvalue('apiDomain')
timeout = form.getvalue('timeout')

req = GSRequest(apiKey, secret, method, params, useHttps, userKey)
req.setAPIDomain(apiDomain)

if timeout != None:
    res = req.send(timeout)
else:
    res = req.send()

# print "HTTP/1.0 200 OK\n";
# print "Content-Type: text/html\n\n\n";
print('x-proxy-log:' + res.getLog().replace("\r\n", " "))

if debug:
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

