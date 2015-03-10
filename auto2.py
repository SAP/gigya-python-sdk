#! /usr/bin/env python
# Import modules for CGI handling 
import cgi, cgitb; cgitb.enable() 
from json import loads as jsonparse
from GSSDK import *
from array import *
import string
import random
import datetime


# Create instance of FieldStorage 
#form = cgi.FieldStorage() 
testFailed = ""
lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(30)]
rand = "".join(lst)

uid = "_gid_HToLRm2508kdYVodGOYlUUcEu6RTBc4OVyi6mnB4B8c=" #"_gid_yhe7dWlNvNxrUmZmZePacw=="
data = "{\"name1\":\"value1\"}"
act = "{ \"title\": \"LOVE IT\",    \"linkBack\": \"http://www.google.com/\",    \"userMessage\": \"test " + rand + "\",    \"description\": \"test kkk description " + rand + "\"}"

method = [ "socialize.getUserInfo", "comments.postComment", "gm.getActionsLog", "accounts.login", "socialize.getFriendsInfo", "ds.store", "socialize.publishUserAction", "chat.getMessages"]

param = [ "{\"UID\":\"" + uid + "\"}", 
          "{\"UID\":\"" + uid + "\",\"categoryID\": \"Test_1\", \"streamID\": \"1069621\", \"commentText\": \"" + rand + "\" }",
          "{\"UID\":\"" + uid + "\"}",
          "{\"loginID\":\"Python5206@live.com\",\"password\":\"Q123456w\"}",
          "{\"UID\":\"" + uid + "\",\"detailLevel\": \"extended\",\"signIDs\": \"true\"}",
          "{\"UID\":\"" + uid + "\",\"data\":" + data + ",\"oid\":\"objid\",\"type\":\"test5206\"}",
          "{\"UID\":\"" + uid + "\",\"userAction\":" + act +"}",
          "{\"UID\":\"" + uid + "\",\"categoryID\": \"44474105\"}"]

# Get data from fields
proxy = "http://192.168.10.245:8888"
apiKey = "2_DJDxNTrvx_QC313MDs_6Byos-ua1lHs5S1-fH32d-MznZn-gLccOid6IYt1D2f26"
partnerSecret = "/erSmRd9Ltf/WqGLmKzycsjWEy9JYvHBNwFfOlpDt/A="
userkey = "AJNfdcZaJ+ap"
secret = "6ApXHw9OvXZdQFFtRNnMNQLWZz8OWTpL"
useHttps = "true"
accessToken = "AT2_25E8C4D60BF10BD81901094AA373BC0E_pT3pp2sSAcs50zIJ_K_y7DzOesnfbrI398UZ4sK-tyfPBxCo0q8zf1sseqJ6I6gAcoyU9-oLDGWmCrs--Ob5HV6nq3wSDsGzp4-EGUFjPECIyy2P8W7U-NK_gonoM_JB"
apiDomain = "us1.gigya.com"

print "Content-Type: text/html\n\n\n"
print "Test started at "
print datetime.datetime.now()
print "</br>"

for p in param:
	pramDic = eval(p)
	m = method[param.index(p)]
	if m == "socialize.getFriendsInfo":
		req = GSRequest(apiKey=accessToken, secretKey="", apiMethod=m, params=pramDic, useHTTPS="false", userKey="")
	else: 
		req = GSRequest(apiKey=apiKey, secretKey=secret, apiMethod=m, params=pramDic, useHTTPS=useHttps, userKey=userkey)
		
	req.setParam("Tester version", "1.0")
	req.setAPIDomain(apiDomain)
	#print 'x-proxy-log:' + res.getLog().replace("\r\n"," ")
	req.setProxy(proxy);
	
	print "Calling " + m + " with params = "
	print req.getParams() 
	print "</br>useHTTPs = " + useHttps
	print "</br></br>"
	
	res = req.send()
	
	print res.getResponseText() + "<br/><br/><br/>"
	print res.getData() 
	print "<br/><br/><br/>"
	
	if res.getErrorCode() != 0:
		testFailed += m + " Error code = " + str(res.getErrorCode()) + " Error code = " + res.getErrorMessage() + " </br>"
	
	if m == "socialize.getUserInfo":
		if SigUtils.validateUserSignature(res.getObject("UID"),res.getObject("signatureTimestamp"),partnerSecret,res.getObject("UIDSignature")):
			print "<br/>userInfo signature test passed</br>"	
		else:
			testFailed += "getUserInfo signature, "				   
	

if SigUtils.validateFriendSignature("_gid_3OqrLttp44M632dM3rHq2g==","1378127128","_gid_HcMGp9pOodeTpGeAPAgH1rYKWVR2xHBmun27uFnMw6s=","/erSmRd9Ltf/WqGLmKzycsjWEy9JYvHBNwFfOlpDt/A=","6s63lo5WyFNJW7XW4kUG8BTUHtc="):
	print "<br/>Friens sig. test passed</br>"
else:
	testFailed += " getFriendsInfo signature test failed, " 

# validateFriendSignature(string UID,string timestamp, string friendUID, string secret, string signature)
	
print "*-------------------------------------------------------------------------------------------------*</br>"
print "Test ended at "
print datetime.datetime.now()
print "</br>"
if testFailed != "":
	print "Autotest failed " + testFailed
else:
	print "Autotest OK"