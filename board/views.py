from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Board, Column, Card, KanbanUser, Category, Topic
import json

def home_view(request):
    if request.session.get('user_id'):
        user = KanbanUser.objects.get(id=request.session['user_id'])
        return redirect(f'/{user.username}/categories/')
    return render(request, "board/home.html")

def login_view(request):
    if request.session.get('user_id'):
        user = KanbanUser.objects.get(id=request.session['user_id'])
        return redirect(f'/{user.username}/categories/')
        
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            user = KanbanUser.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect(f'/{username}/categories/')
        except KanbanUser.DoesNotExist:
            return render(request, "board/login.html", {"error": "Invalid credentials"})
    return render(request, "board/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            return render(request, "board/register.html", {"error": "รหัสผ่านไม่ตรงกัน"})
        
        try:
            KanbanUser.objects.create(username=username, password=password)
            return render(request, "board/register.html", {"success": "สมัครสมาชิกสำเร็จ"})
        except:
            return render(request, "board/register.html", {"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"})
    
    return render(request, "board/register.html")

def kanban_board(request, username, topic_id):
    if not request.session.get('user_id'):
        return redirect("/")
        
    try:
        user = KanbanUser.objects.get(id=request.session['user_id'])
        if user.username != username:
            return redirect("/")
            
        topic = Topic.objects.get(id=topic_id)
        board = Board.objects.get(topic=topic)
        columns = Column.objects.filter(board=board).order_by('order')
        cards = Card.objects.filter(column__board=board).order_by('order')
        
        return render(request, 'board/board.html', {
            'topic': topic,
            'columns': columns,
            'cards': cards,
            'username': username
        })
        
    except (Topic.DoesNotExist, Board.DoesNotExist):
        return redirect('board:categories', username=username)

def category_detail(request, username, category_id):
    if not request.session.get('user_id'):
        return redirect('/')
    
    try:
        category = Category.objects.get(id=category_id)
        topics = Topic.objects.filter(category=category)
        
        return render(request, 'board/category_detail.html', {
            'category': category,
            'topics': topics,
            'username': username
        })
    except Category.DoesNotExist:
        return redirect('board:categories', username=username)

@csrf_exempt
def create_topic(request, username, category_id):
    if request.method == "POST":
        if not request.session.get('user_id'):
            return JsonResponse({'status': 'error', 'message': 'Not logged in'})
        
        data = json.loads(request.body)
        topic_name = data.get('name')
        category = Category.objects.get(id=category_id)
        
        topic = Topic.objects.create(
            category=category,
            name=topic_name
        )
        
        # สร้าง Board สำหรับ Topic นี้
        board = Board.objects.create(
            topic=topic,
            name=topic_name
        )
        
        # สร้าง Columns สำหรับ Board
        columns = ['todo', 'doing', 'done']
        for i, title in enumerate(columns):
            Column.objects.create(board=board, title=title, order=i)
        
        return JsonResponse({
            'status': 'success',
            'topic_id': topic.id,
            'name': topic.name
        })

@csrf_exempt
def create_category(request, username):
    if request.method == "POST":
        if not request.session.get('user_id'):
            return JsonResponse({'status': 'error', 'message': 'Not logged in'})
        
        data = json.loads(request.body)
        category_name = data.get('name')
        user = KanbanUser.objects.get(id=request.session['user_id'])
        category = Category.objects.create(user=user, name=category_name)
        
        return JsonResponse({
            'status': 'success',
            'category_id': category.id,
            'name': category.name
        })
    
def list_categories(request, username):
    if not request.session.get('user_id'):
        return redirect('/')
    
    user = KanbanUser.objects.get(id=request.session['user_id'])
    categories = Category.objects.filter(user=user)
    
    return render(request, 'board/categories.html', {
        'categories': categories,
        'username': username
    })

def update_card(request , username):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_id = data.get('cardId')
        new_column_id = data.get('columnId')
        new_order = data.get('order')
        
        card = Card.objects.get(id=card_id)
        card.column_id = new_column_id
        card.order = new_order
        card.save()
        
        return JsonResponse({'status': 'success'})

@csrf_exempt
@require_http_methods(["POST"])
def add_card(request ,username):
    try:
        data = json.loads(request.body)
        column_id = data.get('columnId')
        content = data.get('content', 'New Task')
        
        # Debug print
        print(f"Received request to add card: Column ID: {column_id}, Content: {content}")
        
        # Get the column
        try:
            column = Column.objects.get(id=column_id)
        except Column.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'Column with id {column_id} not found'
            }, status=404)
        
        # Get the last order number
        last_order = Card.objects.filter(column=column).count()
        
        # Create new card
        card = Card.objects.create(
            column=column,
            content=content,
            order=last_order
        )
        
        print(f"Created new card with ID: {card.id}")
        
        return JsonResponse({
            'status': 'success',
            'cardId': card.id
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error adding card: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
def logout_view(request):
    if request.session.get('user_id'):
        del request.session['user_id']
    return redirect('/')