#!/usr/bin/python
import os
import sys
import logging
project_path = os.path.dirname(__file__)
if project_path not in sys.path:
    sys.path.append(project_path)
from app import app as application
