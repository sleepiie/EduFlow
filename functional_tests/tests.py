from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from board.models import KanbanUser, Category, Topic, Board, Column
from django.contrib.auth.hashers import make_password
import time


class usertest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_hompage_correctly(self):
        #แทนเลยกดเข้าเว็บ
        #แทนเจอหัวข้อเว็บเขียนว่า EduFlow และคำอธิบายของเว็บ และปุ่ม login
        self.browser.get(self.live_server_url)
        self.assertIn('EduFlow', self.browser.title)

        hero_section = self.browser.find_element(By.CLASS_NAME, 'hero-section')
        self.assertIn('Welcome to EduFlow', hero_section.text)
        self.assertIn('เว็บไซต์สำหรับช่วยบริหารจัดการเวลาเรียนเพื่อให้การเรียนมีประสิทธิภาพมากขึ้น', self.browser.find_element(By.CLASS_NAME, 'description').text)

        ##เช็คปุ่ม login และ register
        self.assertTrue(
            self.browser.find_element(By.CLASS_NAME, 'login-btn').is_displayed()
        )
        self.assertTrue(
            self.browser.find_element(By.CLASS_NAME, 'register-btn').is_displayed()
        )
        time.sleep(1)

    def test_can_register(self):
        #แทนลองกดปุ่ม login
        self.browser.get(f"{self.live_server_url}/login/")
        #หน้าเว็บแสดงหน้าต่างล็อกอิน และ สมัครสมาชิก
        login_section = self.browser.find_element(By.CLASS_NAME, 'login-container')
        self.assertIn('Login', login_section.text)
        #แทนกดสมัครสมาชิก และกรอกข้อมูลตามช่องต่างๆ แล้วกดปุ่มสมัครสมาชิก
        link = self.browser.find_element(By.LINK_TEXT, "สมัครสมาชิก")
        link.click()

        ##กรอกข้อมูล
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        confirm_password_input = self.browser.find_element(By.NAME, 'confirm_password')

        username_input.send_keys('tanny')
        password_input.send_keys('GJK67891P4R')
        confirm_password_input.send_keys('GJK67891P4R')

        self.browser.find_element(By.TAG_NAME, 'button').click()

        success_message = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        self.assertIn('สมัครสมาชิกสำเร็จ', success_message.text)
        time.sleep(1)

    def test_can_login(self):
        hash_password = make_password('GJK67891P4R')
        KanbanUser.objects.create(username='tanny', password=hash_password)

        #แทนกลับไปยังหน้าล็อกอินแล้วใส่ username และ password
        self.browser.get(f"{self.live_server_url}/login/")

        ##กรอกข้อมูล
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('tanny')
        password_input.send_keys('GJK67891P4R')
        self.browser.find_element(By.TAG_NAME, 'button').click()

        #หน้าเว็บเปลี่ยนไปยังหน้าหลัก โดยมีด้านขวาบนแสดงชื่อ username และมีปุ่มสำหรับสร้างหมวดหมู่
        user_info = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-dropdown-toggle='dropdown-user']"))
        )
        self.assertIn('tanny', user_info.text)
        self.assertTrue(
            self.browser.find_element(By.CLASS_NAME, 'action-buttons').is_displayed()
        )
        time.sleep(1)

    def test_core_feature(self):
        hash_password = make_password('GJK67891P4R')
        KanbanUser.objects.create(username='tanny', password=hash_password)
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('tanny')
        password_input.send_keys('GJK67891P4R')
        self.browser.find_element(By.TAG_NAME, 'button').click()

        #แทนกดสร้างหมวดหมู่
        #หน้าเว็บแสดงป๊อปอัพให้ใส่ชื่อหมวดหมู่ที่ต้องการ
        create_category_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "create-category-button"))
        )
        create_category_btn.click()

        #แทนใส่ชื่อบอร์ดว่า "Learn management"
        alert = Alert(self.browser)
        alert.send_keys("Learn management")
        alert.accept()

        #หน้าเว็บอัพเดทและแสดงหมวดหมู่ขึ้นมาที่หน้าหลัก
        category_link = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Learn management"))
        )
        self.assertTrue(category_link.is_displayed())
        
        #แทนกดเข้าไปในหมวดหมู่
        category_link.click()

        #แทนเจอปุ่ม "Create Board" แทนเลยลองกดปุ่ม "Create Board"
        create_topic_btn = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.action-buttons button'))
        )
        create_topic_btn.click()

        #หน้าเว็บก็แสดงหน้าต่างสำหรับกรอกหัวข้อในหมวดหมู่นั้นขึ้นมา
        alert = Alert(self.browser)
        alert.send_keys("English")
        alert.accept()

        #แทนใส่ชื่อหัวข้อว่า "English"
        board_link = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "English"))
        )      

        #แทนกดเข้าไปในหัวข้อ English 
        board_link.click()

        #แทนเจอหน้า board ที่มี column todo , doing , done
        columns = self.browser.find_elements(By.CLASS_NAME, 'column')
        column_titles = [col.find_element(By.TAG_NAME, 'h3').text for col in columns]
        
        self.assertEqual(len(columns), 3)
        self.assertIn('todo', column_titles)
        self.assertIn('doing', column_titles)
        self.assertIn('done', column_titles)

        #ทดสอบการแก้ไข task
        first_column = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "column"))
        )
        add_task_btn = first_column.find_element(By.CLASS_NAME, "add-card-btn")
        add_task_btn.click()

        #กดปุ่มสร้าง task
        new_task = WebDriverWait(first_column, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )

        new_task.click()

         #รอ modal ขึ้นมา
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "card-modal"))
        )


        title_input = self.browser.find_element(By.ID, "card-title")
        content_textarea = self.browser.find_element(By.ID, "card-content")
        due_date_input = self.browser.find_element(By.ID, "card-due-date")
        subtask_add_btn = self.browser.find_element(By.ID, "add-subtask-btn")
        
         #กรอกข้อมูล task
        title_input.clear()
        title_input.send_keys("Test Card")
        content_textarea.clear()
        content_textarea.send_keys("This is test detail")
        due_date_input.clear()
        self.browser.execute_script("arguments[0].value = '2025-02-17';", due_date_input)
        self.browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", due_date_input)

        #กรอกข้อมูล subtask
        subtask_add_btn.click()
        subtask_input = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "new-subtask-input"))
        )
        subtask_input.send_keys("test subtask")
        subtask_add_btn.click()

        #กด save
        save_button = self.browser.find_element(By.ID, "save-card")
        save_button.click()

        time.sleep(1)

        #เปิด modal อีกครั้ง
        new_task.click()
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "card-modal"))
        )

        #เช็คข้อมูลว่าตรงกับที่กรอกไหม
        updated_title = self.browser.find_element(By.ID, "card-title").get_attribute("value")
        updated_content = self.browser.find_element(By.ID, "card-content").get_attribute("value")
        updated_due_date = self.browser.find_element(By.ID, "card-due-date").get_attribute("value")
        update_subtask = self.browser.find_element(By.CSS_SELECTOR, "#subtasks-container .subtask-item .subtask-title").text


        self.assertEqual(updated_title, "Test Card")
        self.assertEqual(updated_content, "This is test detail")
        self.assertEqual(updated_due_date, "2025-02-17")
        self.assertEqual(update_subtask, "test subtask")

        save_button.click()
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, "card-modal"))
        )


        #ทดสอบแก้ไข task detail
        new_task.click()
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "card-modal"))
        )

        #แก้ไขข้อมูลใน task
        title_input.clear()
        title_input.send_keys("Test Edit")
        content_textarea.clear()
        content_textarea.send_keys("This is test edit")
        due_date_input.clear()
        self.browser.execute_script("arguments[0].value = '2025-03-16';", due_date_input)
        self.browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", due_date_input)

        #ลบ subtask
        subtask_delete = self.browser.find_element(By.CSS_SELECTOR, ".delete-subtask-icon")
        subtask_delete.click()
        WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        alert.accept()
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#subtasks-container .subtask-item"))
        )
        time.sleep(1)
        save_button.click()
        time.sleep(1)


        #เปิด modal อีกครั้งเพื่อเช็คว่าข้อมูลที่แก้ไปถูกต้อง
        new_task.click()
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "card-modal"))
        )

        updated_title = self.browser.find_element(By.ID, "card-title").get_attribute("value")
        updated_content = self.browser.find_element(By.ID, "card-content").get_attribute("value")
        updated_due_date = self.browser.find_element(By.ID, "card-due-date").get_attribute("value")
        update_subtask = self.browser.find_elements(By.CSS_SELECTOR, "#subtasks-container .subtask-item")

        
        self.assertEqual(updated_title, "Test Edit")
        self.assertEqual(updated_content, "This is test edit")
        self.assertEqual(updated_due_date, "2025-03-16")
        self.assertEqual(len(update_subtask), 0)

        time.sleep(1)

        #ทดสอบลบ task
        delete_task_btn = self.browser.find_element(By.ID, "delete-card")
        delete_task_btn.click()

        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, "card-modal"))
        )

        tasks = self.browser.find_elements(By.CLASS_NAME, "card")
        self.assertEqual(len(tasks), 0)

        time.sleep(1)