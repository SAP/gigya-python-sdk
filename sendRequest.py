# Import modules for CGI handling 
import cgi, cgitb; cgitb.enable() 
from json import loads as jsonparse
from GSSDK import *


# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
apiKey = form.getvalue('apiKey')
debug  = form.getvalue('debug')
if (debug==None):
	debug  = 0
secret  = form.getvalue('secret')
method  = form.getvalue('method')
params  = form.getvalue('params')
useHttps = form.getvalue('useHttps') == "1" or form.getvalue('useHttps') == "true"
userKey = form.getvalue('userKey')
apiDomain = form.getvalue('apiDomain')
timeout = form.getvalue('timeout')

#print 'x-proxy-log:' + res.getLog().replace("\r\n"," ")

if (not params) or (len(params) == 0):
	pramDic = {}
else:
	pramDic = jsonparse(params,encoding="utf-8")	

	print "Content-Type: text/html\n\n\n"


req = GSRequest(apiKey, secret, method, pramDic, useHttps, userKey)
req.setAPIDomain(apiDomain)

if timeout != None:
	res = req.send(timeout)
else:
	res = req.send()

#print "HTTP/1.0 200 OK\n";
#print "Content-Type: text/html\n\n\n";
print 'x-proxy-log:' + res.getLog().replace("\r\n"," ")

if debug:
	print "<h1>response</h1>"
	print "<textarea style='width:100%;height:300px'>"
	print res.getResponseText()
	print "</textarea>"
	print "<h1>Log</h1>"
	print "<textarea style='width:100%;height:500px'>"
	print res.getLog()
	print "</textarea>"
else:
	print res.getResponseText()

