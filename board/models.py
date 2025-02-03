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
    content = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return f"{self.content[:20]}... - {self.column.title}"

    class Meta:
        ordering = ['order']