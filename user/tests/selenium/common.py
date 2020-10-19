from selenium import webdriver
from user.tests.factories import UserFactory
from django.urls import reverse
import time
from faker import Faker
from user.models import User, Driver
from user.providers import CustomPhoneProvider
from phonenumber_field.phonenumber import PhoneNumber


class Common(object):
    def Register(driver):
        fake = Faker()
        fake.add_provider(CustomPhoneProvider)
        driver.get("http://localhost:8080" + reverse('account_signup'))
        time.sleep(2)

        email_field = driver.find_element_by_id("id_email")
        email_field.click()
        email_field.clear()
        email = fake.email()
        email_field.send_keys(email)

        firstname_field = driver.find_element_by_id("id_firstname")
        firstname_field.click()
        firstname_field.clear()
        firstname_field.send_keys(fake.first_name())

        lastname_field = driver.find_element_by_id("id_lastname")
        lastname_field.click()
        lastname_field.clear()
        lastname_field.send_keys(fake.last_name())

        password1_field = driver.find_element_by_id("id_password")
        password1_field.click()
        password1_field.clear()
        password = fake.password()
        password1_field.send_keys(password)

        password2_field = driver.find_element_by_id("id_password2")
        password2_field.click()
        password2_field.clear()
        password2_field.send_keys(password)

        phone_field = driver.find_element_by_id("id_phone")
        phone_field.click()
        phone_field.clear()
        phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164
        phone_field.send_keys(phone)


        # image_field = driver.find_element_by_id("id_image")
        # image_field.send_keys(
        #     r"E:\Picture\Happy birthday Esther ❤️ 20200120_105048.jpg")

        driver.find_element_by_id("register").click()
        driver.get("http://localhost:8080" + reverse('driver_profile_update'))
        
        try:
            all_users = User.objects.all()
            user = all_users.filter(email=email).first()
        except User.DoesNotExist:
            user = Driver.objects.filter(email=email).first()
        return user

    def Login(user):
        driver.get("http://localhost:8080" + reverse('account_login'))

        email_field = driver.find_element_by_name("email")
        email_field.click()
        email_field.send_keys(user.email)

        password_field = driver.find_element_by_name("password")
        password_field.click()
        password_field.send_keys(user.password)

        submit_button = driver.find_element_by_id("login")
        submit_button.click()
        return user
