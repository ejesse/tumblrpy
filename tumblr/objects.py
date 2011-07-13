

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
            self.updated = blog['updated']
            self.description = blog['description']
            self.ask = blog['ask']
            try:
                self.ask_anon = blog['ask_anon']
            except:
                pass
            self.likes = blog['likes']

class Post(TumblrObject):
    pass

class Avatar(TumblrObject):
    pass

class Follower(TumblrObject):
    pass

