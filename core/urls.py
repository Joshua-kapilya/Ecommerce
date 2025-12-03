from django.urls import path
from .views import frontpage
from . import views



urlpatterns = [
	path('', frontpage, name='frontpage'),
	path('category/<int:id>/', views.category_detail, name='category_detail'),

]