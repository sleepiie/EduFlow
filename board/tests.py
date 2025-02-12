from django.test import TestCase , Client
from datetime import date
from django.urls import reverse 
from django.http import HttpRequest 
from board.models import KanbanUser,Category,Topic ,Board , Column , Card , SubTask

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

class ColumnModelTest(TestCase):
    def setUp(self):
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.topic = Topic.objects.create(category=self.category, name="Test Topic")
        self.board = Board.objects.create(topic=self.topic, name="Test Board")

    def test_create_column(self):
        column = Column.objects.create(board=self.board, title="Test Column", order=1)

        self.assertEqual(column.title, "Test Column")
        self.assertEqual(column.board.name, "Test Board")
        self.assertEqual(column.order, 1)
        self.assertEqual(str(column), "Test Column - Test Board")



class CardModelTest(TestCase):
    def setUp(self):
        # สร้างข้อมูลทดสอบเบื้องต้น
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.topic = Topic.objects.create(category=self.category, name="Test Topic")
        self.board = Board.objects.create(topic=self.topic, name="Test Board")
        self.column = Column.objects.create(board=self.board, title="Test Column", order=1)

    def test_create_card(self):
        # ทดสอบการสร้าง Card
        card = Card.objects.create(
            column=self.column,
            title="Test Card",
            content="This is a test card",
            order=1,
            due_date=date(2023, 12, 31)  # ใช้ date object แทนสตริง
        )

        # ตรวจสอบว่าข้อมูลถูกสร้างถูกต้องหรือไม่
        self.assertEqual(card.title, "Test Card")
        self.assertEqual(card.content, "This is a test card")
        self.assertEqual(card.order, 1)
        self.assertEqual(card.due_date.strftime('%Y-%m-%d'), '2023-12-31')  # ตรวจสอบ due_date
        self.assertEqual(card.column.title, "Test Column")
        self.assertEqual(str(card), "Test Card - Test Column")  # ตรวจสอบ __str__


class SubTaskModelTest(TestCase):
    def setUp(self):
        # สร้างข้อมูลทดสอบเบื้องต้น
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.topic = Topic.objects.create(category=self.category, name="Test Topic")
        self.board = Board.objects.create(topic=self.topic, name="Test Board")
        self.column = Column.objects.create(board=self.board, title="Test Column", order=1)
        self.card = Card.objects.create(column=self.column, title="Test Card", order=1)

    def test_create_subtask(self):
        # ทดสอบการสร้าง SubTask
        subtask = SubTask.objects.create(
            card=self.card,
            title="Test Subtask",
            completed=False,
            order=1
        )

        # ตรวจสอบว่าข้อมูลถูกสร้างถูกต้องหรือไม่
        self.assertEqual(subtask.title, "Test Subtask")
        self.assertFalse(subtask.completed)
        self.assertEqual(subtask.order, 1)
        self.assertEqual(subtask.card.title, "Test Card")
        self.assertEqual(str(subtask), "Test Subtask")  # ตรวจสอบ __str__

    def test_subtask_ordering(self):
        # ทดสอบการเรียงลำดับของ SubTask
        subtask1 = SubTask.objects.create(card=self.card, title="Subtask 1", order=1)
        subtask2 = SubTask.objects.create(card=self.card, title="Subtask 2", order=2)
        subtasks = SubTask.objects.all()

        # ตรวจสอบว่าการเรียงลำดับถูกต้องหรือไม่
        self.assertEqual(list(subtasks), [subtask1, subtask2])

    def test_subtask_foreign_key_to_card(self):
        # ทดสอบความสัมพันธ์ ForeignKey ระหว่าง SubTask และ Card
        subtask = SubTask.objects.create(card=self.card, title="Test Subtask", order=1)
        self.assertEqual(subtask.card, self.card)
        self.assertEqual(subtask.card.column, self.column)

    def test_subtask_default_completed_value(self):
        # ทดสอบค่า default ของ completed
        subtask = SubTask.objects.create(card=self.card, title="Test Subtask", order=1)
        self.assertFalse(subtask.completed)  # ตรวจสอบว่า completed เป็น False โดย default