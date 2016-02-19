#!/usr/bin/env python
import json
import cStringIO
import pycurl
import sys

def getDataFromHwDb():
    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://hwcollect.cern.ch:9000/hwinfo/_design/hwhost/_view/cpu_information')
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 2)
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/json'])
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.SSLCERT, '/etc/grid-security/hostcert.pem')
    c.setopt(pycurl.SSLKEY, '/etc/grid-security/hostkey.pem')
    try:
        c.perform()
        answer=buf.getvalue()
        buf.close()
        print >> sys.stderr, "HW DB Poll Succeeded"
        return answer
    except pycurl.error, error:
        errno, errstr = error
        print  >> sys.stderr, 'An error occurred while doing the HW DB Poll: ', errstr 
        exit(1)

def collect_hepspecs():
    stdout_value = json.loads(commands.getoutput(
        r'''meter-cli -m 13273 --start "2015-07-01 00:00:00" -n "hepspec-jmakai" --limit 10000 --json'''
    ))
    return stdout_value
