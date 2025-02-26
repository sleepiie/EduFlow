from django.db import models

class KanbanUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Category(models.Model):
    user = models.ForeignKey(KanbanUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=100)

# แก้ไขโมเดล Board
class Board(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name="board")
    name = models.CharField(max_length=100)



class Column(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.board.name}"

class Card(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name="cards")
    title = models.CharField(max_length=200, default="New Card")  # ฟิลด์ใหม่สำหรับชื่อ card
    content = models.TextField(blank=True)  # รายละเอียด card (สามารถเว้นว่างได้)
    order = models.IntegerField()
    due_date = models.DateField(null=True, blank=True)  # ฟิลด์ due date
    notification_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.column.title}"

    class Meta:
        ordering = ['order']

class SubTask(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']