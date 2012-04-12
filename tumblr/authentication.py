import httplib,urllib
import time
import oauth2 as oauth
from oauth2 import to_unicode,to_utf8,to_unicode_if_string,to_utf8_if_string,to_utf8_optional_iterator
from urllib2 import Request, urlopen
from tumblr.errors import TumblrError
import logging

log = logging.getLogger('tumblr')

REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
AUTHORIZE_URL = 'http://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
BASE_SERVER = 'api.tumblr.com:80'

def to_postdata(params):
    """Serialize as post data for a POST request."""
    d = {}
    for k, v in params.iteritems():
        d[k.encode('utf-8')] = to_utf8_optional_iterator(v)

    # tell urlencode to deal with sequence values and map them correctly
    # to resulting querystring. for example self["k"] = ["v1", "v2"] will
    # result in 'k=v1&k=v2' and not k=%5B%27v1%27%2C+%27v2%27%5D
    return urllib.urlencode(d, True).replace('+', '%20')

class TumblrAuthenticator(oauth.Client):

    request_token_url = REQUEST_TOKEN_URL
    authorization_url_base = AUTHORIZE_URL
    access_token_url = ACCESS_TOKEN_URL
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    
    
    def __init__(self,oauth_consumer_key,secret_key,access_token=None):
        self.oauth_consumer_key=None
        self.secret_key=None
        self.authorize_url = None
        self.request_token = None
        self.access_token = None
        self.consumer = None
        self.oauth_consumer_key=oauth_consumer_key
        self.secret_key=secret_key
        self.consumer = oauth.Consumer(self.oauth_consumer_key, self.secret_key)
        self.connection = httplib.HTTPConnection(BASE_SERVER)
        if access_token is not None:
            self.access_token = access_token
        else:
            """ just go get the request token and auth URL so the dev doesn't have so many steps """
            self.request_token = self.get_request_token()
            self.authorize_url = self.get_authorization_url()

    def get_authorization_url(self):
        request = oauth.Request.from_token_and_callback(token=self.request_token, http_url=self.authorization_url_base)

        return request.to_url()

    def get_request_token(self):
        """
        Get the URL that the user can use to approve the request
        """
        url = self.request_token_url
        request = oauth.Request.from_consumer_and_token(self.consumer, http_url=url)
        request.sign_request(self.signature_method, self.consumer, None)
        resp = urlopen(Request(url, headers=request.to_header()))
        out = resp.read()
        self.request_token = oauth.Token.from_string(out) 
        return self.request_token

    def get_access_token(self, verifier=None):
        """
        After user has authorized the request token, get access token
        with user supplied verifier.
        """
        try:
            # build request
            self.request_token.set_verifier(verifier)
            client = oauth.Client(self.consumer, self.request_token)
            
            resp, content = client.request(self.access_token_url, "POST")
            
            log.debug("access token attempt returned: %s" % (resp))
            self.access_token = oauth.Token.from_string(content)
            return self.access_token
        except Exception, e:
            log.error("Failed to get access token: %s" % (e))
        
    def make_oauth_request(self, url, method, parameters={}, headers={}):
        
        if self.access_token is None:
            raise TumblrError('authenticator does not have a an access token, call get_authorization_url, have the user hit the URL, then call get_access_token, then you can make oauth requests')
        try:
            log.debug("Making OAuth %s to %s with parameters %s" % (method,url,parameters))
            oauth_request = oauth.Request.from_consumer_and_token(self.consumer, token=self.access_token, http_method=method, http_url=url, parameters=parameters)
            oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)
            oauth_headers = oauth_request.to_header()
            headers.update(oauth_headers)
            headers['Accept'] = "text/plain"
            if method.lower() == 'post':
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            else:
                params = urllib.urlencode(parameters)
                url = "%s?%s" % (url,params)

            print headers
            print url
            resp = urlopen(Request(url, headers=headers))
            return resp.read()
        except Exception, e:
            log.error('Failed to send request: %s' % e)
        
    def make_oauth_post(self,url,parameters={},headers={}):
        if self.access_token is None:
            raise TumblrError('authenticator does not have a an access token, call get_authorization_url, have the user hit the URL, then call get_access_token, then you can make oauth requests')
        try:
            oauth_request = oauth.Request.from_consumer_and_token(self.consumer, token=self.access_token, http_method='POST', http_url=url, parameters=parameters)
            oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)
            oauth_headers = oauth_request.to_header()
            headers.update(oauth_headers)
            headers['Accept'] = "text/json"
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
            headers['Expect'] = '100-continue'
            
            self.connection.set_debuglevel(1)
            self.connection.request('POST', url, body=to_postdata(parameters), headers=headers)
            response = self.connection.getresponse()
            return response.read()
        except Exception, e:
            log.error('Failed to send request: %s' % e)
        
        
        
        

        