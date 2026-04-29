import sys
import os

# Add project directory to Python path
project_home = '/home/yourname/soccer-prediction'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Add web directory to path
web_dir = os.path.join(project_home, 'web')
if web_dir not in sys.path:
    sys.path = [web_dir] + sys.path

# Import Flask app
from app import app as application

# Make sure the app is in production mode
application.config['DEBUG'] = False
