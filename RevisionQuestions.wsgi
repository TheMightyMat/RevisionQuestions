#RevisionQuestions.wsgi
import sys
sys.path.insert(0, '/var/www/html/RevisionQuestions')

from api import app as application
