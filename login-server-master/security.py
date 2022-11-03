#This file handles some security issues. 
from flask import request
from app import app
from urllib.parse import urljoin, urlparse
from flask_wtf.csrf import CSRFProtect

#Add CSP header:
@app.after_request
def add_security_headers(resp):
    resp.headers['Content-Security-Policy']='default-src \'self\''
    return resp

#A function that ensures that a redirect target will lead to the same server:
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc
           
#CSRF attack protection.
csrf = CSRFProtect() 
csrf.init_app(app)