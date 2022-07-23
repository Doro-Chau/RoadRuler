from urllib import response
from django.test import TestCase
import requests

# Create your tests here.
def test_map():
    url = 'http://127.0.0.1:8000/'
    response = requests.get(url)
    assert response.status_code == 200