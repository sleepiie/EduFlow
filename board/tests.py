from django.test import TestCase , Client
from django.urls import reverse 
from django.http import HttpRequest 
from board.models import KanbanUser

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
