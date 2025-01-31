from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time


class usertest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_login_page(self):
        self.browser.get(self.live_server_url)

        #แทนเข้าเว็บมาเจอหัวข้อเว็บเขียนว่า EduFlow
        self.assertIn("EduFlow", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text  
        self.assertIn("EduFlow", header_text)

        login_button = self.browser.find_element(By.TAG_NAME,"button").text
        self.assertIn("Login", login_button)

        time.sleep(2)

    def test_can_register(self):
        self.browser.get(self.live_server_url)
        #แทนกดปุ่มสมัครสามาชิก
        time.sleep(2)

        register_link = self.browser.find_element(By.LINK_TEXT, "สมัครสมาชิก")
        register_link.click()

        header_text = self.browser.find_element(By.TAG_NAME, "h2").text  
        self.assertIn("Register", header_text)

        
        time.sleep(2)

        
    