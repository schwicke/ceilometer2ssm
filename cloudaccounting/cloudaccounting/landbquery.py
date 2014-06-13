#!/usr/bin/python
# suds example for calling IT-CS webservice at https://network.cern.ch/soap/
import json
from types import *
from suds.client import Client 
from suds.sax.element import Element
from suds.xsd.doctor import ImportDoctor, Import

def getSerialNumber(username,password,host):
    serial_number=None
    try:
        type = 'CERN'
        url = 'https://network.cern.ch/sc/soap/soap.fcgi?v=5&WSDL'
        imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
        d = ImportDoctor(imp)
        client = Client(url, doctor=d, cache=None)
        token = client.service.getAuthToken(username,password,type)
        authTok = Element('token').setText(token)
        authHeader = Element('Auth').insert(authTok)
        client.set_options(soapheaders=authHeader)
        result=client.service.vmGetInfo(host);
        vmParent=result['VMParent']
        result=client.service.getDeviceInfo(vmParent)
        serial_number=result['SerialNumber']
        print serial_number
    except:
        print >> sys.stderr, "Error Occured while contacting the landb database"
    return serial_number

