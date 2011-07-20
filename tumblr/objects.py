import datetime
import logging

from tumblr.errors import TumblrError
from tumblr.utils import dict_to_object_value

log = logging.getLogger('tumblr')

class TumblrObject(object):
    api=None
    
    def __init__(self,api=None):
        if api is not None:
            self.api = api
    
    def __string__(self):
        return 'this tumblr object is not properly identifying itself, open an issue at https://github.com/ejesse/tumblrpy/issues'        
    
    def __repr__(self):
        return '%s %s' % (self.__class__.__name__,self.__string__())

class TumblrUser(TumblrObject):
    name=None
    likes = 0
    following=0
    default_post_format='html'
    blogs=[]

    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('name',self,data_dict)
            dict_to_object_value('likes',self,data_dict)
            dict_to_object_value('following',self,data_dict)
            dict_to_object_value('default_post_format',self,data_dict)
            if data_dict.has_key('blogs'):
                for blog_dict in data_dict['blogs']:
                    blog = Blog(api=api,data_dict=blog_dict)
                    self.blogs.append(blog)
            super(TumblrUser,self).__init__(api=api)

    def __string__(self):
        return "%s" % (self.name)

class Blog(TumblrObject):
    url=None
    title = None
    num_posts = None
    name = None
    updated = None
    description = None
    ask = False
    ask_anon = False
    likes = None
    posts = None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('title',self,data_dict)
            dict_to_object_value('num_posts',self,data_dict)
            dict_to_object_value('name',self,data_dict)
            dict_to_object_value('updated',self,data_dict,type='datetime')
            dict_to_object_value('description',self,data_dict)
            dict_to_object_value('ask',self,data_dict)
            dict_to_object_value('ask_anon',self,data_dict)
            dict_to_object_value('likes',self,data_dict)
            dict_to_object_value('url',self,data_dict)

        super(Blog,self).__init__(api=api)
            
    def get_posts(self):
        if self.posts is None:
            if not '.' in self.name:
                name = '%s%s' % (self.name,'.tumblr.com')
            else:
                name = self.name
            self.api.get_posts(name)
    
    def __string__(self):
        return "%s %s" % (self.name,self.title)

class TumblrPhotoSize(TumblrObject):
    url = None
    height=None
    width=None
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            dict_to_object_value('url',self,data_dict)
            dict_to_object_value('width',self,data_dict,type='int')
            dict_to_object_value('height',self,data_dict,type='int')
        super(TumblrPhotoSize,self).__init__(api=api)

    
class TumblrPhoto(TumblrObject):
    caption = None
    alt_sizes = []
    width=None
    height=None
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('caption',self,data_dict)
            dict_to_object_value('width',self,data_dict,type='int')
            dict_to_object_value('height',self,data_dict,type='int')
            if data_dict.has_key('alt_sizes'):
                try:
                    sizes = data_dict['alt_sizes']
                    for size in sizes:
                        p = TumblrPhotoSize(api=api,data_dict=size)
                        self.alt_sizes.append(p)
                except:
                    message = "%s %s" % ('failed to set alternate photo sizes from value')
                    log.warn(message)
            else:
                log.warn('no alt_sizes found in PhotoPost photo object')

        super(TumblrPhoto,self).__init__(api=api)

class Post(TumblrObject):
    
    blog_name=None
    id=None
    post_url=None
    type=None
    timestamp=None
    date=None
    format=None
    reblog_key=None
    tags=None
    bookmarket=False
    mobile=False
    source_url=None
    source_title=None
    total_posts=None
    ## submission only fields
    tweet=False
    markdown=False

    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            dict_to_object_value('blog_name',self,data_dict)
            dict_to_object_value('id',self,data_dict)
            dict_to_object_value('post_url',self,data_dict)
            dict_to_object_value('type',self,data_dict)
            dict_to_object_value('timestamp',self,data_dict)
            dict_to_object_value('date',self,data_dict)
            dict_to_object_value('format',self,data_dict)
            dict_to_object_value('reblog_key',self,data_dict)
            dict_to_object_value('tags',self,data_dict)
            dict_to_object_value('bookmarket',self,data_dict)
            dict_to_object_value('mobile',self,data_dict)
            dict_to_object_value('source_url',self,data_dict)
            dict_to_object_value('source_title',self,data_dict)
            dict_to_object_value('total_posts',self,data_dict)
        super(Post,self).__init__(api=api)
        
    def __string__(self):
        return '%s post with id %s at ' % (self.type,self.id,self.url)
    
    def delete(self):
        pass

class TextPost(Post):
    
    type='text'
    title=None
    body=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('title',self,data_dict)
            dict_to_object_value('body',self,data_dict)
        super(TextPost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title
    
    def save(self):
        if not self.api:
            raise TumblrError("Can't save. %s Object was instantiated without an API instance." % (self.__class__.__name__))
        self.api.update_edit_post(self)

class PhotoPost(Post):
    
    photos=[]
    caption=None
    width=None
    height=None
    
    ## submission fields
    link=None
    source=None
    data=None
    
    def __init__(self,api=None,data_dict=None):
        
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            if data_dict.has_key('photos'):
                try:
                    photo_list = data_dict['photos']
                    for photo in photo_list:
                        p = TumblrPhoto(api=api,data_dict=photo)
                        self.photos.append(p)
                except:
                    message = "%s %s" % ('failed to set photo list from value')
                    log.warn(message)
            else:
                log.warn('no photos found in PhotoPost')
        super(PhotoPost,self).__init__(api=api,data_dict=data_dict)
    
    def __string__(self):
        return self.caption
    
#    def save(self):
#        if self.api is None:
#            log.error("No API instance passed into object, so I can't save, did you work around the API?")
#        self.api.

class QuotePost(Post):
    
    type='quote'
    text=None
    source=None
    
    ## submission fields
    quote=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('text',self,data_dict)
            dict_to_object_value('source',self,data_dict)
        super(QuotePost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title

class LinkPost(Post):
    
    type='link'
    title=None
    url=None
    description=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('title',self,data_dict)
            dict_to_object_value('url',self,data_dict)
            dict_to_object_value('description',self,data_dict)
        super(LinkPost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title
    
class ChatPost(Post):
    
    type='chat'
    title=None
    body=None
    dialogue=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('title',self,data_dict)
            dict_to_object_value('body',self,data_dict)
            dict_to_object_value('dialogue',self,data_dict)
        super(ChatPost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title
    
class AudioPost(Post):
    
    type='audio'
    caption=None
    player=None
    plays=None
    album_art=None
    artist=None
    album=None
    track_name=None
    track_number=None
    year=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('caption',self,data_dict)
            dict_to_object_value('player',self,data_dict)
            dict_to_object_value('plays',self,data_dict,type='int')
            dict_to_object_value('album_art',self,data_dict)
            dict_to_object_value('artist',self,data_dict)
            dict_to_object_value('album',self,data_dict)
            dict_to_object_value('track_name',self,data_dict)
            dict_to_object_value('track_number',self,data_dict,type='int')
            dict_to_object_value('year',self,data_dict)
        super(AudioPost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title
    
class VideoPost(Post):
    
    type='video'
    caption=None
    body=None
    player=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for %s' % (self.__class__.__name__))
            dict_to_object_value('caption',self,data_dict)
            dict_to_object_value('body',self,data_dict)
            self.player = data_dict['player']
        super(VideoPost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title
    
class AnswerPost(Post):

    asking_name=None
    asking_url=None
    question=None
    answer=None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for TextPost')
            dict_to_object_value('asking_name',self,data_dict)
            dict_to_object_value('asking_url',self,data_dict)
            dict_to_object_value('question',self,data_dict)
            dict_to_object_value('answer',self,data_dict)
        super(AnswerPost,self).__init__(api=api,data_dict=data_dict)
        
    def __string__(self):
        return self.title

class Avatar(TumblrObject):
    
    def __init__(self,api=None,data_dict=None):
        raise TumblrError("sorry, avatar objects aren't done yet")


class Follower(TumblrUser):
    
    url = None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            log.debug('attempting to populate data for Follower')
            dict_to_object_value('url',self,data_dict)
        super(Follower,self).__init__(api=api,data_dict=data_dict)
        

