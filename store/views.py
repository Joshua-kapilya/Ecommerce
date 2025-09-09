from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Products
from django.db.models import Q
from django.shortcuts import redirect

from .cart import Cart
from .forms import OrderForm
# Create your views here.

def product_detail(request, product_id):
	product = Products.objects.get(id=product_id)
	cart = Cart(request)
	print(cart.get_total_cost())
	return render(request, 'store/product_detail.html', {'product':product})


def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)

    return redirect('frontpage')

def cart_view(request):
	cart = Cart(request)

	return render(request, 'store/cart_view.html', { 'cart':cart } )


def get_total_cost(self):
	for p in self.cart.keys():
		self.cart[str(p)]['product'] = Product.objects.get(pk=p)

	return int(sum(item['product'].price * item['quantity'] for item in self.cart.values())) / 100

def clear(self):
	del self.session[settings.CART_SESSION_ID]
	self.session.modified = True

def change_quantity(request, product_id):
	action = request.GET.get('action', '')

	if action:
		quantity = 1
		if action == 'decrease':
			quantity = -1
		else:
			if action == 'increase':
				quantity = +1
		cart = Cart(request)
		cart.add(product_id, quantity, True)



	return redirect('cart_view')


def remove_from_cart(request, product_id):
	cart = Cart(request)
	cart.remove(product_id)

	return redirect('cart_view')

@login_required
def checkout(request):
	if request.method == 'POST':
		form = OrderForm(request)
		if form.is_valid():
			total_price = 0

			for item in cart:
				product = item ['product']

				total_price += product.price * int(item['quantity'])

			order = form.save()
			order.created_by = request.user
			order.paid_amount = total_price
			order.save()

			for item in cart:
				product = item['product']
				quantity = int(item['quantity'])
				price = product.price * quantity

				item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)

			cart.clear()




			return redirect('myaccount')

	else:
		form = OrderForm()
	cart = Cart(request)
	
	return render(request, 'store/checkout.html', { 'cart':cart, 'form': form } )


def search (request):
	query = request.GET.get('query', '')
	products = Products.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

	return render(request, 'store/search.html',  {'products': products, 'query':query})




@login_required
def my_store_order_detail(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'userprofile/my_store_order_detail.html', {'order': order})

