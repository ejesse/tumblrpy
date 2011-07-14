import datetime

class TumblrObject():
    pass

class TumblrUser(TumblrObject):
    pass

class Blog(TumblrObject):
    title = None
    num_posts = None
    name = None
    updated = None
    description = None
    ask = False
    ask_anon = False
    likes = None
    
    def __init__(self,api=None,data_dict=None):
        if data_dict is not None:
            blog = data_dict['blog']
            self.title = blog['title']
            self.num_posts = blog['posts']
            self.name = blog['name']
            self.updated = datetime.datetime.fromtimestamp(blog['updated'])
            self.description = blog['description']
            self.ask = blog['ask']
            try:
                self.ask_anon = blog['ask_anon']
            except:
                pass
            self.likes = blog['likes']
            
    def get_posts(self):
        ## TODO FIXME go and get posts for the blog
        pass

class Post(TumblrObject):
    pass

class TextPost(Post):
    pass

class PhotoPost(Post):
    pass

class QuotePost(Post):
    pass

class LinkPost(Post):
    pass

class ChatPost(Post):
    pass

class AudioPost(Post):
    pass

class VideoPost(Post):
    pass

class AnswerPost(Post):
    pass

class Avatar(TumblrObject):
    pass

class Follower(TumblrObject):
    pass

