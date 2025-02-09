from django.test import TestCase , Client
from django.urls import reverse 
from django.http import HttpRequest 
from board.models import KanbanUser,Category,Topic ,Board

# Create your tests here.
class Login_test(TestCase):
    def test_user(self):
        #create test user
        user = KanbanUser.objects.create(username = "testuser" , password = "testpass1234")
        self.assertEqual(user.username,"testuser" )
        self.assertEqual(user.password , "testpass1234")
        self.assertEqual(str(user), "testuser") 

    def test_login_page(self):
        #create login view
        client = Client()
        response = client.get(reverse('board:login')) 
        
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'board/login.html')  
        self.assertIn("<title>EduFlow</title>", response.content.decode())

class CategoryModelTest(TestCase):
    def setUp(self):
        # สร้างผู้ใช้สำหรับการทดสอบ
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")

    def test_create_category(self):
        # สร้างหมวดหมู่ที่เชื่อมโยงกับผู้ใช้
        category = Category.objects.create(user=self.user, name="Test Category")
        
        # ตรวจสอบว่าหมวดหมู่ถูกสร้างถูกต้องหรือไม่
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.user.username, "testuser")

class TopicModelTest(TestCase):
    def setUp(self):
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")
        self.category = Category.objects.create(user=self.user, name="Test Category")

    def test_create_topic(self):
        topic = Topic.objects.create(category=self.category, name="Test Topic")
        

        self.assertEqual(topic.name, "Test Topic")
        self.assertEqual(topic.category.name, "Test Category")


class BoardModelTest(TestCase):
    def setUp(self):
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.topic = Topic.objects.create(category=self.category, name="Test Topic")

    def test_create_board(self):
        board = Board.objects.create(topic=self.topic, name="Test Board")

        self.assertEqual(board.name, "Test Board")
        self.assertEqual(board.topic.name, "Test Topic")