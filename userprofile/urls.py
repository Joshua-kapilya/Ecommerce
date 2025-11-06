from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('my-store/add-product/', views.add_product, name='add_product'),
	path('my-store/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
	path('my-store/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
	path('mystore/', views.mystore, name='mystore'),
	path('signup', views.signup, name='signup'),
	path('login/', auth_views.LoginView.as_view(template_name='userprofile/login.html'), name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('myaccount/', views.myaccount, name='myaccount'),
	path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
	path('become_vendor', views.become_vendor, name='become_vendor'),
	path('order/<int:order_id>/', views.order_detail, name='order_detail'),
	path('confirm-received/<int:item_id>/', views.confirm_received, name='confirm_received'),
	path('edit-profile/', views.edit_profile, name='edit_profile'),
	path('completed-orders/', views.completed_orders, name='completed_orders'),
	path('pending-earnings/', views.pending_earnings, name='pending_earnings'),
	path('available-balance/', views.available_balance, name='available_balance')
]