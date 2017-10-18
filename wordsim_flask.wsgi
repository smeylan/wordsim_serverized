import sys
import os
wordsim_serverized_path = "/var/www/wordsim_serverized/"
sys.path.insert(0, wordsim_serverized_path)

activate_this = os.path.join(wordsim_serverized_path, 'ws-serverized/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

def application(environ, start_response):
	os.environ['WORDSIM_SERVERIZED_PATH'] = wordsim_serverized_path
	from wordsim_flask import app as _application
	return _application(environ, start_response)

