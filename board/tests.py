from django.test import TestCase, Client
from datetime import date
from django.urls import reverse
from board.models import KanbanUser, Category, Topic, Board, Column, Card, SubTask

# Create your tests here.
class KanbanTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = KanbanUser.objects.create(username="testuser", password="testpass123")
        self.category = Category.objects.create(user=self.user, name="Test Category")
        self.topic = Topic.objects.create(category=self.category, name="Test Topic")
        self.board = Board.objects.create(topic=self.topic, name="Test Board")
        self.column = Column.objects.create(board=self.board, title="Test Column", order=1)
        self.card = Card.objects.create(column=self.column, title="Test Card", order=1)
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(str(self.user), "testuser")
    
    def test_login_page(self):
        response = self.client.get(reverse('board:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/login.html')
        self.assertIn("<title>EduFlow</title>", response.content.decode())
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.user.username, "testuser")
    
    def test_topic_creation(self):
        self.assertEqual(self.topic.name, "Test Topic")
        self.assertEqual(self.topic.category.name, "Test Category")
    
    def test_board_creation(self):
        self.assertEqual(self.board.name, "Test Board")
        self.assertEqual(self.board.topic.name, "Test Topic")
    
    def test_column_creation(self):
        self.assertEqual(self.column.title, "Test Column")
        self.assertEqual(self.column.board.name, "Test Board")
        self.assertEqual(self.column.order, 1)
    
    def test_card_creation(self):
        card = Card.objects.create(
            column=self.column, title="Another Card", content="This is another test card", order=2,
            due_date=date(2023, 12, 31)
        )
        self.assertEqual(card.title, "Another Card")
        self.assertEqual(card.due_date.strftime('%Y-%m-%d'), '2023-12-31')
    
    def test_subtask_creation(self):
        subtask = SubTask.objects.create(card=self.card, title="Test Subtask", order=1)
        self.assertEqual(subtask.title, "Test Subtask")
        self.assertFalse(subtask.completed)
        self.assertEqual(subtask.card.title, "Test Card")
    
    def test_subtask_ordering(self):
        subtask1 = SubTask.objects.create(card=self.card, title="Subtask 1", order=1)
        subtask2 = SubTask.objects.create(card=self.card, title="Subtask 2", order=2)
        self.assertEqual(list(SubTask.objects.all()), [subtask1, subtask2])
