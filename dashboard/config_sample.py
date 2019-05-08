import os
basedir = os.path.abspath(os.path.dirname(__file__))

TMPDIR = os.path.join(basedir, '..', 'tmp')

DEFAULT_TOKEN_DURATION = 600 #IN SECONDS

WTF_CSRF_ENABLED = True
SECRET_KEY = 'heytheredonottrytomesswithmemister2'

# GAMEEVENTS_SERVICE_ENDPOINT = 'http://gameevents.mairacarvalho.com/v1'
# USERPROFILE_SERVICE_ENDPOINT = 'http://userprofile.mairacarvalho.com/v1'

GAMEEVENTS_SERVICE_ENDPOINT = 'http://localhost:5000/v1'
USERPROFILE_SERVICE_ENDPOINT = 'http://localhost:5002/v1'
LEARNINGANALYSIS_SERVICE_ENDPOINT = 'http://localhost:5003/v1'



# Hard-code disabling CDN support:
BOOTSTRAP_SERVE_LOCAL = True

DEBUB = True
