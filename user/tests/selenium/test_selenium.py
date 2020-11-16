from selenium import webdriver
from django.test import TestCase
import time
import pytest
from user.models import User, Driver, Vehicle 
from faker import Faker
import random
from random import randint
from django.urls import reverse
import time

fake = Faker()


@pytest.mark.skip
class TestUpdateViewMixin(TestCase):
    def setUp(self):
        # for x in range(20):
        #     driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        #     phone=fake.numerify(text='080########'), 
        #     is_driver=True)
        #     driver_user.set_password("password")
        #     driver_user.save()
        #     driver = Driver.objects.filter(user=driver_user).first()
        #     driver.location= fake.random_element(elements=driver.City.values)
        #     driver.status = 'AV'
        #     driver.journey_type = fake.random_elements(elements=driver.Journey_type.values, unique=True)
        #     driver.vehicle.name = "old name"
        #     driver.vehicle.plate_number = "old plate number"
        #     driver.vehicle.color = "old color"
        #     driver.vehicle.capacity = fake.random_int(min=1, max=20)
        #     driver.vehicle.vehicle_type = fake.random_element(elements=Vehicle.Vehicle_type.values)
        #     driver.save()
        #     driver.vehicle.save()
        self.driver = webdriver.Chrome(
            executable_path="E:\PC PROGRAMS\chromedriver_win32\chromedriver")

        self.driver.get("http://localhost:8000" + reverse('account_signup'))

        email_field = self.driver.find_element_by_id("id_email")
        email_field.click()
        email_field.clear()
        email = fake.email()
        email_field.send_keys(email)

        firstname_field = self.driver.find_element_by_id("id_firstname")
        firstname_field.click()
        firstname_field.clear()
        firstname_field.send_keys(fake.first_name())

        lastname_field = self.driver.find_element_by_id("id_lastname")
        lastname_field.click()
        lastname_field.clear()
        lastname_field.send_keys(fake.last_name())

        password1_field = self.driver.find_element_by_id("id_password")
        password1_field.click()
        password1_field.clear()
        password = "Ukoemma5050."
        password1_field.send_keys(password)

        password2_field = self.driver.find_element_by_id("id_password2")
        password2_field.click()
        password2_field.clear()
        password2_field.send_keys(password)

        phone_field = self.driver.find_element_by_id("id_phone")
        phone_field.click()
        phone_field.clear()
        phone=fake.numerify(text='080########')
        phone_field.send_keys(phone)
        
        dob_field = self.driver.find_element_by_id('id_date_of_birth')
        dob_field.click()
        dob_field.clear()
        dob_field.send_keys('4/5/2002')

        referral_field = self.driver.find_element_by_id("id_referral")
        referral_field.click()
        referral_field.clear()
        referral_field.send_keys('elishae621@gmail.com')

        self.driver.find_element_by_id("register").click()

        self.driver.get("http://localhost:8000" + reverse('account_logout'))
        sign_out_button = self.driver.find_element_by_tag_name("button")
        sign_out_button.click()

        self.driver.get("http://localhost:8000" + reverse('account_login'))
        
        email_field = self.driver.find_element_by_id("id_login")
        email_field.click()
        email_field.clear()
        email_field.send_keys(email)
        
        password_field = self.driver.find_element_by_id("id_password")
        password_field.click() 
        password_field.clear()
        password_field.send_keys(password)

        login_button = self.driver.find_element_by_id("login")
        login_button.click()

        time.sleep(5)
        # self.driver.get("http://localhost:8080" + reverse('create_request'))
        
        # from_address_field = self.driver.find_element_by_id("id_from_address")
        # from_address_field.click()
        # from_address_field.clear()
        # from_address_field.send_keys(fake.address())

        # city_field = random.choices([
        #     self.driver.find_element_by_id("id_city_1"),
        #     self.driver.find_element_by_id("id_city_2"),
        #     self.driver.find_element_by_id("id_city_3"),
        #     self.driver.find_element_by_id("id_city_4")
        # ])
        # city_field[0].click()

        # intercity_field = self.driver.find_element_by_id("id_intercity")        
        # for c in range(2):
        #     if c == 0:
        #         intercity_field.click()

        # request_vehicle_type_field = random.choices([
        #     self.driver.find_element_by_id("id_request_vehicle_type_1"),
        #     self.driver.find_element_by_id("id_request_vehicle_type_2"),
        #     self.driver.find_element_by_id("id_request_vehicle_type_3")
        # ])
        # request_vehicle_type_field[0].click()
        
        # no_of_passengers_field = self.driver.find_element_by_id("id_no_of_passengers")
        # no_of_passengers_field.click()
        # no_of_passengers_field.clear()
        # no_of_passengers_field.send_keys(randint(1, 20))

        # load_field = self.driver.find_element_by_id("id_load")        
        # for c in range(2):
        #     if c == 0:
        #         load_field.click()

        # self.driver.find_element_by_id("request").click()

        # self.driver.get("http://localhost:8080/" + reverse('price_confirmation'))
        # time.sleep(5)
        # self.driver.find_element_by_id("proceed").click()
    

    def test_register_and_login(self):
        self.assertIn("Dot360s", self.driver.title)
