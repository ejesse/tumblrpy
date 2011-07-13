import simplejson
import urllib
import urllib2
from tumblr.errors import TumblrError
from tumblr.utils import to_unicode_or_bust
from tumblr.objects import Blog
from tumblr.authentication import TumblrAuthenticator


class TumblrAPI():
    
    authenticator = None
    api_base = 'http://api.tumblr.com/v2'
    print_json = False
    
    def __init__(self,oauth_consumer_key=None,secret_key=None,authenticator=None,print_json=False):
        if print_json:
            self.print_json = print_json
        if authenticator is not None:
            self.authenticator = authenticator
        if oauth_consumer_key is not None and secret_key is not None and authenticator is not None:
            raise TumblrError("You don't need to pass in the consumer key, the secret and an authenticator. Either the keys OR an authenticator. Thanks, I get confused if you pass me all three.")
        if oauth_consumer_key is not None and secret_key is not None and authenticator is None:
            self.authenticator = TumblrAuthenticator(oauth_consumer_key,secret_key)

    def __check_for_tumblr_error__(self,json):
        error_text = 'Unknown Tumblr error'
        result = simplejson.loads(json)
        if result.has_key('meta'):
            if result['meta'].has_key('status'):
                if int(result['meta']['status']) >= 400:
                    if result['meta'].has_key('msg'): 
                        error_text = result['meta']['msg']
                    raise TumblrError('An error was returned from Tumblr API: %s' % (error_text))    

    def __get_request_unauthenticated__(self,endpoint,data):
        params = urllib.urlencode(data)
        full_uri = "%s?%s" % (endpoint,params)
        try:
            response = urllib2.urlopen(full_uri)
        except urllib2.HTTPError, e:
            raise TumblrError(e.__str__())
        response_text = response.read()
        response_text = to_unicode_or_bust(response_text, 'iso-8859-1')
        if self.print_json:
            print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __get_request_key_authenticated__(self,endpoint,data):
        try:
            data['api_key'] = self.authenticator.oauth_consumer_key
        except:
            raise TumblrError('This method requires instantiating the TumblrAPI with an oauth_consumer_key and secret_key or a TumblrAuthenticator')
        params = urllib.urlencode(data)
        full_uri = "%s?%s" % (endpoint,params)
        try:
            response = urllib2.urlopen(full_uri)
        except urllib2.HTTPError, e:
            raise TumblrError(e.__str__())
        response_text = response.read()
        response_text = to_unicode_or_bust(response_text, 'iso-8859-1')
        if self.print_json:
            print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __get_request_oauth_authenticated__(self,endpoint,data):
        pass
    
    def __post_request_unauthenticated__(self,endpoint,data):
        pass
    
    def __post_request_key_authenticated__(self,endpoint,data):
        pass
    
    def __post_request_oauth_authenticated__(self,endpoint,data):
        pass
    
    def get_blog_info(self,blog_name):
        if (blog_name is None):
            raise TumblrError("please pass in a blog name (e.g. ejesse.tumblr.com)")
        
        parameters = {}
        
        endpoint = self.api_base + '/blog/' + blog_name + '/info'
        
        returned_json = self.__get_key_authenticated__(endpoint, parameters)
        blog_dict = simplejson.loads(returned_json)
        blog = Blog(api=self,data_dict=blog_dict['response'])
        return blog
