from flask import Flask
import os
app = Flask(__name__)
#config = os.path.join(app.root_path, 'settings.cfg')
#app.config.from_pyfile(config)
#app.config.from_object('config')

from app import views
