from app import app
from caapi import apiv1
from flask import abort,make_response,request
from datetime import date, datetime, timedelta
from calendar import monthrange
from time import localtime, strftime
from dateutil import parser
import json
@app.route('/',methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    str =  {"Help": "List of APIs avalable"}
    str['v1.0/tenant'] = {"Help": "It provides cloud accounting information for all Tenants within start and end date",
                        "request_data_format": '{"startdate":"yyyy-mm-dd","enddate":"yyyy-mm-dd"}',
                        "methods" : "POST"
                       }
    str['v1.0/tenant/<tenant_id>'] = {"Help": "It provides cloud accounting information for specific Tenant within start and end date",
                        "request_data_format": '{"startdate":"yyyy-mm-dd","enddate":"yyyy-mm-dd"}',
                        "methods" : "POST"
                       }
    str['v1.0/vo'] = {"Help": "It provides cloud accounting information for all VOs within start and end date",
                        "request_data_format": '{"startdate":"yyyy-mm-dd","enddate":"yyyy-mm-dd"}',
                        "methods" : "POST"
                       }
    str['v1.0/vo/<vo_name>'] = {"Help": "It provides cloud accounting information for specific VO within start and end date",
                        "request_data_format": '{"startdate":"yyyy-mm-dd","enddate":"yyyy-mm-dd"}',
                        "methods" : "POST"
                       }
    str['v1.0/vm'] = {"Help": "It provides cloud accounting information for all VMs within start and end date",
                        "request_data_format": '{"startdate":"yyyy-mm-dd","enddate":"yyyy-mm-dd"}',
                        "methods" : "POST"
                       }
    str = json.dumps(str, sort_keys=True,indent=4, separators=(',', ': '))
    return str

@app.route('/v1.0/tenant', methods = ['GET','POST'])
def resource_tenants_wise():
    if not request.json or not 'startdate' in request.json or not 'enddate' in request.json:
        abort(400)
    starttime = str(request.json['startdate']) + " 00:00:00"
    endtime = str(request.json['enddate']) + " 23:59:59"
    try:
        start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
        end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return make_response(json.dumps( { 'error': 'Invalid date format, should be "YYYY-MM-DD"' } ), 404)
    result = apiv1.daily_resource_tenant_wise(start_time_obj,end_time_obj)
    return result

@app.route('/v1.0/tenant/<tenant_id>', methods = ['GET','POST'])
def resource_tenant_wise(tenant_id):
    if not request.json or not 'startdate' in request.json or not 'enddate' in request.json:
        abort(400)
    starttime = str(request.json['startdate']) + " 00:00:00"
    endtime = str(request.json['enddate']) + " 23:59:59"
    try:
        start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
        end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return make_response(json.dumps( { 'error': 'Invalid date format, should be "YYYY-MM-DD"' } ), 404)
    result = apiv1.daily_resource_tenant_wise(start_time_obj, end_time_obj, tenant_id)
    return result

@app.route('/v1.0/vo', methods = ['GET','POST'])
def resource_vos_wise():
    if not request.json or not 'startdate' in request.json or not 'enddate' in request.json:
        abort(400)
    starttime = str(request.json['startdate']) + " 00:00:00"
    endtime = str(request.json['enddate']) + " 23:59:59"
    try:
        start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
        end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return make_response(json.dumps( { 'error': 'Invalid date format, should be "YYYY-MM-DD"' } ), 404)
    result = apiv1.daily_resource_vo_wise(start_time_obj,end_time_obj)
    return result

@app.route('/v1.0/vo/<vo_name>', methods = ['GET','POST'])
def resource_vo_wise(vo_name):
    if not request.json or not 'startdate' in request.json or not 'enddate' in request.json:
        abort(400)
    starttime = str(request.json['startdate']) + " 00:00:00"
    endtime = str(request.json['enddate']) + " 23:59:59"
    try:
        start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
        end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return make_response(json.dumps( { 'error': 'Invalid date format, should be "YYYY-MM-DD"' } ), 404)
    result = apiv1.daily_resource_vo_wise(start_time_obj, end_time_obj, vo_name)
    return result

@app.route('/v1.0/vm', methods = ['GET','POST'])
def resource_vm_wise():
    if not request.json or not 'startdate' in request.json or not 'enddate' in request.json:
        abort(400)
    starttime = str(request.json['startdate']) + " 00:00:00"
    endtime = str(request.json['enddate']) + " 23:59:59"
    try:
        start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
        end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return make_response(json.dumps( { 'error': 'Invalid date format, should be "YYYY-MM-DD"' } ), 404)
    result = apiv1.daily_resource_vm_wise(start_time_obj,end_time_obj)
    return result

@app.errorhandler(404)
def not_found(error):
    return make_response(json.dumps( { 'error': 'Resource not found' } ), 404)
