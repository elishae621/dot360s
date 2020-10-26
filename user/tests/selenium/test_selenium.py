from selenium import webdriver
from django.test import TestCase
from user.tests.selenium.common import Common
import time
import pytest


@pytest.mark.skip
class TestUpdateViewMixin(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(
            executable_path="E:\PC PROGRAMS\chromedriver_win32/chromedriver")
        Common.Register(driver=self.driver)
        time.sleep(10)

    def test_register_and_login(self):
        self.assertIn("dot360s", self.driver.title)
