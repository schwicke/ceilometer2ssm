import os
import sys
import json
basedir = os.path.abspath(os.path.dirname(__file__))

def read_config():
    filename="/etc/ceilodata.conf"
    try:
        f = open(filename,"r")
        try:
            result= json.loads(f.read())
            f.close
            return result
        except:
            print >> sys.stderr, 'ERROR: Cannot parse configuration file ' + filename
            exit(1)
    except IOError:
        print >> sys.stderr, 'ERROR: Cannot open configuration file ' + filename
        exit(1)

config=read_config()
dbuser=config['database']['user']
dbpwd=config['database']['password']
database_name=config['database']['database_name']
MYSQL_URL = "mysql://"+dbuser+":"+dbpwd+"@localhost:3306/cloudaccounting"    
