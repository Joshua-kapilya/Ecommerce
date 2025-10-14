from django.contrib import admin
from .models import Category, Products, Order, OrderItem

# Register your models here.
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Order)
admin.site.register(OrderItem)

from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "owner__username")
    list_editable = ("is_approved",)  # ✅ lets you approve directly from list view

