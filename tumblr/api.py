import simplejson
import urllib
import urllib2

from tumblr.errors import TumblrError
from tumblr.utils import to_unicode_or_bust, remove_nones
from tumblr.objects import *
from tumblr.authentication import TumblrAuthenticator
import logging

log = logging.getLogger('tumblr')

class TumblrAPI():
    
    api_base = 'http://api.tumblr.com/v2'
    
    def __init__(self,oauth_consumer_key=None,secret_key=None,authenticator=None,print_json=False,access_token=None,blog_base_hostname=None, request_token=None):
        self.authenticator = None
        self.print_json = False
        self.blog_base_hostname = None
        self.authorized_user=None
        if self.print_json or log.level < 20:
            self.print_json = print_json
        if authenticator is not None:
            self.authenticator = authenticator
        if oauth_consumer_key is not None and secret_key is not None and authenticator is not None:
            raise TumblrError("You don't need to pass in the consumer key, the secret and an authenticator. Either the keys OR an authenticator. Thanks, I get confused if you pass me all three.")
        if oauth_consumer_key is not None and secret_key is not None and authenticator is None:
            log.info('Instantiating TumblrAuthenticator from supplied key and secret')
            self.authenticator = TumblrAuthenticator(oauth_consumer_key,secret_key)
        if access_token is not None:
            if self.authenticator is None:
                self.authenticator = TumblrAuthenticator()
            self.authenticator.access_token = access_token
            self.authorized_user = self.get_user_info()
            if len(self.authorized_user.blogs) == 1:
                self.blog_base_hostname = self.authorized_user.blogs[0].url

        if request_token is not None:
            if self.authenticator is None:
                self.authenticator = TumblrAuthenticator()
            self.authenticator.request_token = request_token

        if blog_base_hostname is not None:
            self.blog_base_hostname = blog_base_hostname
        if self.blog_base_hostname is None:
            log.warn('Not providing a base_hostname will make it near impossible to do any writes to tumblr, authorize a user')
        
            

    def __check_for_tumblr_error__(self,json):
        error_text = 'Unknown Tumblr error'
        if json is None:
            raise TumblrError('An error was returned from Tumblr API: %s' % (error_text))  

        try:           
            result = simplejson.loads(json)
        except Exception, e:
            raise TumblrError("We got an error %s.  The body we got back from Tumblr was %s" % (e, json))

        if result.has_key('meta'):
            if result['meta'].has_key('status'):
                if int(result['meta']['status']) >= 400:
                    if result['meta'].has_key('msg'): 
                        error_text = result['meta']['msg']
                    raise TumblrError('An error was returned from Tumblr API: %s' % (error_text))    

    def __get_request_unauthenticated__(self,endpoint,data):
        data = remove_nones(data)
        params = urllib.urlencode(data)
        full_uri = "%s?%s" % (endpoint,params)
        try:
            response = urllib2.urlopen(full_uri)
        except urllib2.HTTPError, e:
            raise TumblrError(e.__str__())
        response_text = response.read()
        response_text = to_unicode_or_bust(response_text, 'iso-8859-1')
        #if self.print_json or log.level < 20:
        #    print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __make_authenticated_request__(self,endpoint,data,method):
        try:
            data['api_key'] = self.authenticator.oauth_consumer_key
        except:
            raise TumblrError('This method requires instantiating the TumblrAPI with an oauth_consumer_key and secret_key or a TumblrAuthenticator')
        data = remove_nones(data)
        
        if method.lower() == 'get':
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
        #if self.print_json:
        #    print response_text
        self.__check_for_tumblr_error__(response_text)
        return response_text
    
    def __get_request_key_authenticated__(self,endpoint,data):
        return self.__make_authenticated_request__(endpoint,data,'GET')
    
    def __make_oauth_request__(self,endpoint,data,method):
        try:
            access_token = self.authenticator.access_token
        except:
            raise TumblrError('This method requires obtaining and access token')
        #params = urllib.urlencode(data)
        data = remove_nones(data)
        log.debug('making %s request to %s with parameters %s' % (method,endpoint,data))
        
        response_text = self.authenticator.make_oauth_request(endpoint, method, parameters=data)

        log.debug('raw response: %s' % (response_text))
        response_text = to_unicode_or_bust(response_text, 'iso-8859-1')
        #if self.print_json:
        #    print response_text
        self.__check_for_tumblr_error__(response_text)
        
        return response_text
    
    def __get_request_oauth_authenticated__(self,endpoint,data):
        return self.__make_oauth_request__(endpoint, data, 'GET')
    
    def __post_request_unauthenticated__(self,endpoint,data):
        pass
    
    def __post_request_key_authenticated__(self,endpoint,data):
        return self.__make_authenticated_request__(endpoint,data,'GET')
    
    def __post_request_oauth_authenticated__(self,endpoint,data):
        return self.__make_oauth_request(endpoint, data, 'POST')
    
    def get_authorization_url(self):
        return self.authenticator.get_authorization_url()
    
    def get_access_token(self,verifier=None):
        """ convenience method """
        if verifier is None:
            raise TumblrError("Can't get an access token without a verifier")
        access_token = self.authenticator.get_access_token(verifier=verifier)
        ## go get the user info, makes other things easier later
        self.authorized_user = self.get_user_info()
        if self.blog_base_hostname is None:
            if len(self.authorized_user.blogs) == 1:
                self.blog_base_hostname = self.authorized_user.blogs[0].url 
        return access_token
    
    def get_user_info(self):
        if self.authenticator.access_token is None:
            raise TumblrError("User info method requires a valid access token")
        
        endpoint = self.api_base + '/user/info'
        
        returned_json = self.__get_request_oauth_authenticated__(endpoint, {})
        data_dict = simplejson.loads(returned_json)
        
        user_dict = data_dict['response']['user']
        user = TumblrUser(api=self,data_dict=user_dict)
        
        return user


    def get_user_dashboard(self, **kwargs):
        endpoint = self.api_base + '/user/dashboard'
        parameters = {}
        for arg in kwargs:
            parameters[arg] = kwargs[arg]

        returned_json = self.__get_request_oauth_authenticated__(endpoint, parameters)
        data_dict = simplejson.loads(returned_json)
        return data_dict


    def get_blog_info(self,blog_name=None):
        if (blog_name is None and self.blog_base_hostname is None):
            raise TumblrError("please pass in a blog name (e.g. ejesse.tumblr.com)")
        if blog_name is None:
            blog_name = self.blog_base_hostname
            
        blog_name = blog_name.replace('http://','')
        blog_name = blog_name.replace('/','')
        parameters = {}
        
        endpoint = self.api_base + '/blog/' + blog_name + '/info'
        
        returned_json = self.__make_authenticated_request__(endpoint, parameters,'GET')
        data_dict = simplejson.loads(returned_json)
        
        log.debug('Returned JSON: %s' % (returned_json))
        
        blog_dict = data_dict['response']['blog']
        blog = Blog(api=self,data_dict=blog_dict)
        return blog
    
    def get_blog(self,blog_name=None):
        return self.get_blog_info(blog_name)
    
    def get_posts(self,blog_name=None, type=None,id=None,tag=None,limit=None,offset=None,reblog_info=None,notes_info=None,format=None):
        if (blog_name is None and self.blog_base_hostname is None):
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
        if reblog_info is not None:
            parameters['rebog_info'] = reblog_info
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
        
        if self.blog_base_hostname is None:
            raise TumblrError("Set a blog_base_hostname on your API instance so we know which blog we're trying to talk to. No, you cannot at this time get this info from an OAuth Key")
        
        parameters = {}
        
        parameters['type'] = post.type
        parameters['tags'] = post.tags
        parameters['tweet'] = False
        if post.date is None:
            parameters['date'] = datetime.datetime.now()
        parameters['markdown']=False
        
        log.debug('Post type is %s' % (post.type))
        
        if post.type.lower() == 'text':
            parameters['title'] = post.title
            parameters['body'] = post.body
        
        blog_base_hostname = self.blog_base_hostname.replace("http://","")
        
        endpoint = "%s/blog/%spost" % (self.api_base,blog_base_hostname)
        
        if post.id is not None:
            endpoint = endpoint + 'edit'
        
        r = self.__make_oauth_request__(endpoint, parameters, 'POST')
            
        return r
    
    def delete_post(self,post=None,id=None):
        if post is None and id is None:
            raise TumblrError("Pass in a post or id, otherwise what are you deleting?")
        elif post is not None:
            if post.id is None:
                raise TumblrError("The supplied Post object has no id")
    
    def get_followers(self,blog_name=None,limit=None,offset=None):
        if (blog_name is None and self.blog_base_hostname is None):
            raise TumblrError("please pass in a blog name (e.g. ejesse.tumblr.com)")
        if blog_name is None:
            blog_name = self.blog_base_hostname
            
        blog_name = blog_name.replace('http://','')
        blog_name = blog_name.replace('/','')
        
        parameters = {}
        
        if limit is not None:
            parameters['limit'] = limit
        if offset is not None:
            parameters['offset'] = offset
        
        endpoint = self.api_base + '/blog/' + blog_name + '/followers'
        
        returned_json = self.__make_oauth_request__(endpoint, parameters,'GET')
        data_dict = simplejson.loads(returned_json)
        
        log.debug('Returned JSON: %s' % (returned_json))
        
        followers_dict = data_dict['response']['users']
        followers = []
        for f_dict in followers_dict:
            follower = Follower(api=self,data_dict=f_dict)
            followers.append(follower)
        return followers
        
        
        
    def follow(self,blog_url):
        
        blog_url = blog_url.replace('http://','')
        blog_url = blog_url.replace('/','')
        
        parameters = {'url' : blog_url}
        
        endpoint = self.api_base + '/user/follow'
        try:
            returned_json = self.__make_oauth_request__(endpoint, parameters,'POST')
            log.debug('following %s result: %s' % (blog_url,returned_json))
        except TumblrError:
            return False
        return True
    
    def unfollow(self,blog_url):
        
        blog_url = blog_url.replace('http://','')
        
        parameters = {'url' : blog_url}
        
        endpoint = self.api_base + '/user/unfollow'
        try:
            returned_json = self.__make_oauth_request__(endpoint, parameters,'POST')
            log.debug('unfollowing %s result: %s' % (blog_url,returned_json))
        except TumblrError:
            return False
        return True
