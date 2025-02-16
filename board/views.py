from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password, check_password
from .models import Board, Column, Card, KanbanUser, Category, Topic ,SubTask

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
            user = KanbanUser.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                return redirect(f'/{username}/categories/')
            else:
                return render(request, "board/login.html", {"error": "Invalid credentials"})
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
            KanbanUser.objects.create(username=username, password=make_password(password))
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
        user = KanbanUser.objects.get(id=request.session['user_id'])
        all_categories = Category.objects.filter(user=user)
        
        return render(request, 'board/category_detail.html', {
            'category': category,
            'topics': topics,
            'username': username,
            'categories': all_categories
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


@csrf_exempt
@require_http_methods(["POST"])
def edit_card(request, username):
    try:
        data = json.loads(request.body)
        card_id = data.get('cardId')
        title = data.get('title')
        content = data.get('content')
        due_date = data.get('dueDate')  # คาดว่ารูปแบบเป็น 'YYYY-MM-DD'
        card = Card.objects.get(id=card_id)
        card.title = title
        card.content = content
        card.due_date = due_date if due_date != "" else None
        card.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

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
        
        print(f"Received request to add card: Column ID: {column_id}, Content: {content}")
        
        try:
            column = Column.objects.get(id=column_id)
        except Column.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'Column with id {column_id} not found'
            }, status=404)
        
        last_order = Card.objects.filter(column=column).count()
        
        card = Card.objects.create(
            column=column,
            title=content,   
            content="",
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


@csrf_exempt
@require_http_methods(["GET"])
def get_subtasks(request, username, card_id):
    try:
        card = Card.objects.get(id=card_id)
        subtasks = card.subtasks.all().order_by('order')
        data = []
        for st in subtasks:
            data.append({
                'id': st.id,
                'title': st.title,
                'completed': st.completed,
            })
        return JsonResponse({'status': 'success', 'subtasks': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def add_subtask(request, username):
    try:
        data = json.loads(request.body)
        card_id = data.get('cardId')
        title = data.get('title')
        card = Card.objects.get(id=card_id)
        last_order = card.subtasks.count()
        subtask = SubTask.objects.create(card=card, title=title, order=last_order)
        return JsonResponse({'status': 'success', 'subtask': {
            'id': subtask.id,
            'title': subtask.title,
            'completed': subtask.completed,
        }})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_subtask(request, username):
    try:
        data = json.loads(request.body)
        subtask_id = data.get('subtaskId')
        completed = data.get('completed')
        subtask = SubTask.objects.get(id=subtask_id)
        subtask.completed = completed
        subtask.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_subtask(request, username):
    try:
        data = json.loads(request.body)
        subtask_id = data.get('subtaskId')
        subtask = SubTask.objects.get(id=subtask_id)
        subtask.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_card(request, username):
    try:
        data = json.loads(request.body)
        card_id = data.get('cardId')
        card = Card.objects.get(id=card_id)
        card.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def logout_view(request):
    if request.session.get('user_id'):
        del request.session['user_id']
    return redirect('/')