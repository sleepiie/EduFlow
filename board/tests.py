from django.test import TestCase , Client
from django.urls import reverse 
from django.http import HttpRequest 
from board.models import KanbanUser,Category,Topic ,Board , Column ,Card
from django.utils.timezone import now, timedelta
from datetime import date, timedelta
from unittest.mock import patch
from freezegun import freeze_time

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



class NotificationTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = KanbanUser.objects.create(username='testuser', password='testpass')
        
        # Create test category
        self.category = Category.objects.create(user=self.user, name='Test Category')
        
        # Create test topic
        self.topic = Topic.objects.create(category=self.category, name='Test Topic')
        
        # Create test board
        self.board = Board.objects.create(topic=self.topic, name='Test Board')
        
        # Create test column
        self.column = Column.objects.create(board=self.board, title='Test Column', order=0)
        
        # Create test card with due date 5 days from today
        self.today = date.today()
        self.card = Card.objects.create(
            column=self.column,
            title='Test Card',
            due_date=self.today + timedelta(days=5),
            order=0
        )
        
        # Set up test client
        self.client = Client()
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

    def test_notification_display_period(self):
        base_url = f'/{self.user.username}/categories/'
        
        # Test for 7 consecutive days
        for day_offset in range(7):
            current_date = self.today + timedelta(days=day_offset)
            
            with freeze_time(current_date):
                # Make request to categories view
                response = self.client.get(base_url)
                
                # Get filtered cards from context
                filtered_cards = response.context['filtered_card']
                
                # Check if card should be visible
                days_until_due = (self.card.due_date - current_date).days
                should_show = days_until_due < 5  # As per view logic
                
                # Verify card presence
                self.assertEqual(
                    self.card in filtered_cards,
                    should_show,
                    f"Day +{day_offset} (Due in {days_until_due} days): "
                    f"Card should{'' if should_show else ' not'} be visible"
                )
                
                # Verify session date tracking
                session = self.client.session
                self.assertEqual(
                    session.get('last_visit_date'),
                    current_date.strftime('%Y-%m-%d'),
                    "Session should track last visit date correctly"
                )