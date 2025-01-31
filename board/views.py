from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Board, Column, Card, KanbanUser
import json

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            user = KanbanUser.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect(f'/{username}/board')
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
            return redirect('/')  # กลับไปหน้า login หลังสมัครสำเร็จ
        except:
            return render(request, "board/register.html", {"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"})
    
    return render(request, "board/register.html")

def kanban_board(request, username):
    if not request.session.get('user_id'):
        return redirect("/")
    user = KanbanUser.objects.get(id=request.session['user_id'])
    if user.username != username:
        return redirect("/")
    board, created = Board.objects.get_or_create(user=user)
    
    if created:
        columns = ['To Do', 'In Progress', 'Done']
        for i, title in enumerate(columns):
            Column.objects.create(board=board, title=title, order=i)
    
    columns = Column.objects.filter(board=board).order_by('order')
    cards = Card.objects.filter(column__board=board).order_by('order')
    
    return render(request, "board/board.html", {
        "board": board,
        "columns": columns,
        "cards": cards,
        "username": username
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