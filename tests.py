import unittest
from tumblr.api import TumblrAPI

class TumblrAPITest(unittest.TestCase):
    
    def __init__(self, testname, oauth_consumer_key, secret_key):
        super(TumblrAPITest, self).__init__(testname)
        self.api = TumblrAPI(oauth_consumer_key, secret_key)
    
    def test_blog_info(self):
        blog_name = 'ejesse'
        blog_domain_name = blog_name + '.tumblr.com'
        blog = self.api.get_blog_info(blog_domain_name)
        self.assertEqual(blog.name, blog_name)

if __name__ == '__main__':
    import sys
    oauth_consumer_key = sys.argv[1]
    secret_key = sys.argv[2]

    suite = unittest.TestSuite()
    suite.addTest(TumblrAPITest("test_blog_info", oauth_consumer_key, secret_key))

    unittest.TextTestRunner().run(suite)