from django.urls import path
from . import views


urlpatterns = [
	path('cart-checkout', views.checkout, name='checkout'),
	path('vendor/success/', views.vendor_success, name='vendor_success'),
	path('my-store/product-detail/<int:pk>', views.my_store_order_detail, name='my_store_order_detail'),
	path('change-quantity/<str:product_id>/', views.change_quantity, name='change_quantity'),
	path('search/', views.search, name='search'),
	path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
	path('cart/', views.cart_view, name='cart_view'),
	path('products/<int:product_id>/', views.product_detail, name='product_detail'),
	path('add-to-cart/<product_id>?', views.add_to_cart, name='add_to_cart')

]