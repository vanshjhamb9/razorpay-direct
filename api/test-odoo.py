"""
Vercel serverless function for /test-odoo
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import app

def handler(request):
    """Vercel serverless function handler"""
    environ = {
        'REQUEST_METHOD': request.method or 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path or '/',
        'QUERY_STRING': request.query_string or '',
        'CONTENT_TYPE': request.headers.get('content-type', 'application/json'),
        'CONTENT_LENGTH': str(len(request.body or b'')),
        'SERVER_NAME': request.headers.get('host', 'localhost'),
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body or b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    for key, value in (request.headers or {}).items():
        env_key = 'HTTP_' + key.replace('-', '_').upper()
        environ[env_key] = value
    
    response_data = []
    status_code = [200]
    response_headers = []
    
    def start_response(status, headers):
        status_code[0] = int(status.split()[0])
        response_headers[:] = headers
        return response_data.append
    
    result = app(environ, start_response)
    body = b''.join(result) if result else b''
    
    return {
        'statusCode': status_code[0],
        'headers': dict(response_headers),
        'body': body.decode('utf-8') if isinstance(body, bytes) else body
    }
