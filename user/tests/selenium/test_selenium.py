from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import TestCase, tag
from django.urls import reverse
from user.tests.factories import UserFactory
from user.tests.selenium.common import Common
import time
import pytest


@pytest.mark.skip
class TestUpdateViewMixin(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(
            executable_path="E:\PC PROGRAMS\chromedriver_win32/chromedriver")
        driver = self.driver
        registered_user = Common.Register(driver=driver)

    def test_register_and_login(self):
        self.assertIn("dot360s", driver.title)
