import simplejson
import urllib
import urllib2
from tumblr.errors import TumblrError
from tumblr.utils import to_unicode_or_bust
from tumblr.objects import *
from tumblr.authentication import TumblrAuthenticator
import logging

log = logging.getLogger('tumblr')

class TumblrAPI():
    
    authenticator = None
    api_base = 'http://api.tumblr.com/v2'
    print_json = False
    
    def __init__(self,oauth_consumer_key=None,secret_key=None,authenticator=None,print_json=False):
        if self.print_json or log.level < 20:
            self.print_json = print_json
        if authenticator is not None:
            self.authenticator = authenticator
        if oauth_consumer_key is not None and secret_key is not None and authenticator is not None:
            raise TumblrError("You don't need to pass in the consumer key, the secret and an authenticator. Either the keys OR an authenticator. Thanks, I get confused if you pass me all three.")
        if oauth_consumer_key is not None and secret_key is not None and authenticator is None:
            log.info('Instantiating TumblrAuthenticator from supplied key and secret')
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
        if self.print_json or log.level < 20:
            print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __make_authenticated_request__(self,endpoint,data,method):
        try:
            data['api_key'] = self.authenticator.oauth_consumer_key
        except:
            raise TumblrError('This method requires instantiating the TumblrAPI with an oauth_consumer_key and secret_key or a TumblrAuthenticator')
        if method.lower() is 'get':
            params = urllib.urlencode(data)
            full_uri = "%s?%s" % (endpoint,params)
            log.debug('%s %s' % ('making request to',full_uri))
            try:
                response = urllib2.urlopen(full_uri)
            except urllib2.HTTPError, e:
                raise TumblrError(e.__str__())
        else:
            request = urllib2.Request(endpoint, data)
            if method.lower() is not 'post':
                log.info('making request via %s' % (method))
                request.get_method = lambda: method
            log.debug('making %s request to %s with parameters %s' % (method,endpoint,data))
            response = urllib2.urlopen(request)
            
        response_text = response.read()
        response_text = to_unicode_or_bust(response_text, 'iso-8859-1')
        if self.print_json:
            print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __get_request_key_authenticated__(self,endpoint,data):
        return self.__make_authenticated_request__(self,endpoint,data,'GET')
    
    def __make_oauth_request(self,endpoint,data,method):
        try:
            access_token = self.authenticator.access_token
        except:
            raise TumblrError('This method requires obtaining and access token')
        #params = urllib.urlencode(data)
        log.debug('making %s request to %s with parameters %s' % (method,endpoint,data))
        try:
            response_text = self.authenticator.make_oauth_request(endpoint, method, parameters=data)
        except TumblrError, e:
            log.error('Error mamking OAuth request: %s' % (e))
        
        response_text = to_unicode_or_bust(response_text, 'iso-8859-1')
        if self.print_json:
            print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __get_request_oauth_authenticated__(self,endpoint,data):
        return self.__make_oauth_request(endpoint, data, 'GET')
    
    def __post_request_unauthenticated__(self,endpoint,data):
        pass
    
    def __post_request_key_authenticated__(self,endpoint,data):
        return self.__make_authenticated_request__(self,endpoint,data,'GET')
    
    def __post_request_oauth_authenticated__(self,endpoint,data):
        return self.__make_oauth_request(endpoint, data, 'POST')
    
    def get_blog_info(self,blog_name):
        if (blog_name is None):
            raise TumblrError("please pass in a blog name (e.g. ejesse.tumblr.com)")
        
        parameters = {}
        
        endpoint = self.api_base + '/blog/' + blog_name + '/info'
        
        returned_json = self.__get_request_key_authenticated__(endpoint, parameters)
        data_dict = simplejson.loads(returned_json)
        
        blog_dict = data_dict['response']['blog']
        blog = Blog(api=self,data_dict=blog_dict)
        return blog
    
    def get_blog(self,blog_name):
        return self.get_blog_info(blog_name)
    
    def get_posts(self,blog_name, type=None,id=None,tag=None,limit=None,offset=None,rebog_info=None,notes_info=None,format=None):
        if (blog_name is None):
            raise TumblrError("please pass in a blog name (e.g. ejesse.tumblr.com)")
        
        parameters = {}
        
        if id is not None:
            parameters['id'] = id
        if tag is not None:
            parameters['tag'] = tag
        if limit is not None:
            parameters['limit'] = limit
        if offset is not None:
            parameters['offset'] = offset
        if rebog_info is not None:
            parameters['rebog_info'] = rebog_info
        if notes_info is not None:
            parameters['notes_info'] = notes_info
        if format is not None:
            parameters['format'] = format

        
        type_endpoint=''
        
        if type is not None:
            type_endpoint = '%s%s' % ('/',type)
        
        endpoint = self.api_base + '/blog/' + blog_name + '/posts' + type_endpoint
        
        returned_json = self.__get_request_key_authenticated__(endpoint, parameters)
        data_dict = simplejson.loads(returned_json)
        
        posts_dict = data_dict['response']['posts']
        
        posts = []
        
        for post_dict in posts_dict:
            if post_dict['type'] == 'text':
                try:
                    posts.append(TextPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create TextPost: %s' % (e))
            elif post_dict['type'] == 'photo':
                try:
                    posts.append(PhotoPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create PhotoPost: %s' % (e))
            elif post_dict['type'] == 'quote':
                try:
                    posts.append(QuotePost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create QuotePost: %s' % (e))
            elif post_dict['type'] == 'link':
                try:
                    posts.append(LinkPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create LinkPost: %s' % (e))
            elif post_dict['type'] == 'chat':
                try:
                    posts.append(ChatPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create ChatPost: %s' % (e))
            elif post_dict['type'] == 'audio':
                try:
                    posts.append(AudioPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create AudioPost: %s' % (e))
            elif post_dict['type'] == 'video':
                try:
                    posts.append(VideoPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create VideoPost: %s' % (e))
            elif post_dict['type'] == 'answer':
                try:
                    posts.append(AnswerPost(data_dict=post_dict))
                except Exception, e:
                    log.error('Failed to create TextPost: %s' % (e))
                
        
        return posts
    
    def update_edit_post(self,post):
        
