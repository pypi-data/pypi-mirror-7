from mock import Mock
from django.test import TestCase
from django.test.utils import override_settings

from django_seo_js.middleware import HashBangMiddleware, UserAgentMiddleware



class BaseMiddlewareTest(TestCase):
    pass

class HashBangMiddlewareTest(TestCase):

    @override_settings(SEO_JS_BACKEND='django_seo_js.backends.TestBackend')
    def setUp(self):
        super(HashBangMiddlewareTest, self).setUp()
        self.middleware = HashBangMiddleware()
        self.request = Mock()
        self.request.GET = {}

    def test_has_escaped_fragment(self):
        self.request.GET = {"_escaped_fragment_": None}
        self.assertEqual(self.middleware.process_request(self.request), "Test")

    def test_does_not_have_escaped_fragment(self):
        self.request.GET = {}
        self.assertEqual(self.middleware.process_request(self.request), None)


class UserAgentMiddlewareTest(TestCase):

    
    @override_settings(SEO_JS_BACKEND='django_seo_js.backends.TestBackend')
    def setUp(self):
        super(UserAgentMiddlewareTest, self).setUp()
        self.middleware = UserAgentMiddleware()
        self.request = Mock()
        self.request.META = {}

    def test_matches_one_of_the_default_user_agents(self):
        self.request.META = {
            "HTTP_USER_AGENT": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        }
        self.assertEqual(self.middleware.process_request(self.request), "Test")

    def test_does_not_match_one_of_the_default_user_agents(self):
        self.request.META = {
            "HTTP_USER_AGENT": "This user-agent is not a search engine."
        }
        self.assertEqual(self.middleware.process_request(self.request), None)

    @override_settings(SEO_JS_USER_AGENTS=["TestUserAgent",])
    @override_settings(SEO_JS_BACKEND='django_seo_js.backends.TestBackend')
    def test_overriding_matches(self):
        self.middleware = UserAgentMiddleware()
        self.request.META = {
            "HTTP_USER_AGENT": "The TestUserAgent v1.0"
        }
        self.assertEqual(self.middleware.process_request(self.request), "Test")

    @override_settings(SEO_JS_USER_AGENTS=["TestUserAgent",])
    @override_settings(SEO_JS_BACKEND='django_seo_js.backends.TestBackend')
    def test_overriding_does_not_match_properly(self):
        self.middleware = UserAgentMiddleware()
        self.request.META = {
            "HTTP_USER_AGENT": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        }
        self.assertEqual(self.middleware.process_request(self.request), None)
