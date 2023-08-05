from django.conf import settings
import requests
from base import SEOBackendBase

class TestBackend(SEOBackendBase):
    """Implements a test backend"""

    def get_rendered_page(self, url):
        return "Test"

    def update_url(self, url):
        return "Test worked"