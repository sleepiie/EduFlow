from django.contrib import admin
from .models import KanbanUser, Board, Column, Card

@admin.register(KanbanUser)
class KanbanUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')

admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Card)