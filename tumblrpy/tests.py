import unittest
from api import TumblrAPI

class TumblrAPITest(unittest.TestCase):
    
    def __init__(self, oauth_consumer_key, secret_key):
        super(TumblrAPITest, self).__init__()
        self.api = TumblrAPI(oauth_consumer_key, secret_key)
    
    def setUp(self):
        self.api = TumblrAPI()
    
    def test_blog_info(self):
        blog_name = 'ejesse'
        blog = self.api.get_blog_info(blog_name)
        self.assertEqual(blog.name, blog_name)

if __name__ == '__main__':
    import sys
    oauth_consumer_key = sys.argv[1]
    secret_key = sys.argv[2]

    suite = unittest.TestSuite()
    suite.addTest(TumblrAPITest("test_blog_info", oauth_consumer_key, secret_key))

    unittest.TextTestRunner().run(suite)