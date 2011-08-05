import httplib
import time
import oauth2 as oauth
from urllib2 import Request, urlopen
from tumblr.errors import TumblrError
import logging

log = logging.getLogger('tumblr')

REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
AUTHORIZE_URL = 'http://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
BASE_SERVER = 'www.tumblr.com:80'


class TumblrAuthenticator(oauth.Client):

    oauth_consumer_key=None
    secret_key=None
    request_token_url = REQUEST_TOKEN_URL
    authorization_url_base = AUTHORIZE_URL
    authorize_url = None
    access_token_url = ACCESS_TOKEN_URL
    request_token = None
    access_token = None
    consumer = None
    signature_method = oauth.SignatureMethod_HMAC_SHA1()

    def __init__(self,oauth_consumer_key,secret_key,access_token=None):
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
            url = self.access_token_url

            # build request
            request = oauth.Request.from_consumer_and_token(
                self.consumer,
                token=self.request_token, http_url=url,
                parameters={'verifier':str(verifier)}
            )
            request.sign_request(self.signature_method, self.consumer, self.request_token)

            # send request
            resp = urlopen(Request(url, headers=request.to_header()))
            self.access_token = oauth.OAuthToken.from_string(resp.read())
            return self.access_token
        except Exception, e:
            log.error("Failed to access token: %s" % (e))
        
    def make_oauth_request(self, url, method, parameters={}, headers={}):
        if self.access_token is None:
            raise TumblrError('authenticator does not have a an access token, call get_authorization_url, have the user hit the URL, then call get_access_token, then you can make oauth requests')
        try:
            oauth_request = oauth.Request.from_consumer_and_token(self.consumer, token=self.access_token, http_method=method, http_url=url, parameters=parameters)
            oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)
            req_headers = oauth_request.to_header()
            print req_headers
            for k in req_headers.keys():
                headers[k] = req_headers[k]
#            log.debug("making oauth request %s to URL % with parameters: %s and headers: %s" % (method,url,parameters,req_headers))
            resp = urlopen(Request(url, headers=req_headers))
            return resp.read()
        except Exception, e:
            raise TumblrError('Failed to send request: %s' % e)

        