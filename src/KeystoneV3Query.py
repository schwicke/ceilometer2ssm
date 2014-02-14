import httplib
import json
import os
import urllib
import urlparse
import sys


def print_dbg(*args):
   sys.stderr.write(' '.join(map(str, args)) + '\n')

def getDomains(keystoneserver, token):
   auth_server = urlparse.urlparse(keystoneserver)[1]
   auth_protocol = urlparse.urlparse(keystoneserver)[0]
   auth_path = urlparse.urlparse(keystoneserver)[2].replace('v2.0','v3') + "/domains"
   header  = {'X-Auth-Token': token}
   req = "GET"
   if auth_protocol == "https":
    Newconn = httplib.HTTPSConnection
   else:
    Newconn = httplib.HTTPConnection
   get_auth_conn = Newconn( auth_server )
   get_auth_conn.request( req, auth_path, headers=header)
   answer = get_auth_conn.getresponse()
   if answer.status == 200:
    decoded = json.loads(answer.read())
    return decoded['domains']
   else:
    print_dbg(answer.read())
    print_dbg(answer.reason())

def getProjects(keystoneserver, token):
   auth_server = urlparse.urlparse(keystoneserver)[1]
   auth_protocol = urlparse.urlparse(keystoneserver)[0]
   auth_path = urlparse.urlparse(keystoneserver)[2].replace('v2.0','v3') + "/projects"
   header  = {'X-Auth-Token': token}
   req = "GET"
   if auth_protocol == "https":
    Newconn = httplib.HTTPSConnection
   else:
    Newconn = httplib.HTTPConnection
   get_auth_conn = Newconn( auth_server )
   get_auth_conn.request( req, auth_path, headers=header)
   answer = get_auth_conn.getresponse()
   if answer.status == 200:
    decoded = json.loads(answer.read())
    return decoded['projects']
   else:
    print_dbg(answer.read())
    print_dbg(answer.reason())
 
def getUsers(keystoneserver, token):
   auth_server = urlparse.urlparse(keystoneserver)[1]
   auth_protocol = urlparse.urlparse(keystoneserver)[0]
   auth_path = urlparse.urlparse(keystoneserver)[2].replace('v2.0','v3') + "/users"
   header  = {'X-Auth-Token': token}
   req = "GET"
   if auth_protocol == "https":
    Newconn = httplib.HTTPSConnection
   else:
    Newconn = httplib.HTTPConnection
   get_auth_conn = Newconn( auth_server )
   get_auth_conn.request( req, auth_path, headers=header)
   answer = get_auth_conn.getresponse()
   if answer.status == 200:
    decoded = json.loads(answer.read())
    return decoded['users']
   else:
    print_dbg(answer.read())
    print_dbg(answer.reason())

   

