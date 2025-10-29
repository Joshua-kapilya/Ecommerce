from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Products, Order, OrderItem, Review
from django.db.models import Q
from django.shortcuts import redirect
from .forms import ReviewForm
from django.db import models


from .cart import Cart
from .forms import OrderForm, StoreForm

from userprofile.models import Userprofile  # if you still use Userprofile


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StoreForm

from django.contrib import messages

# store/views.py
def vendor_success(request):
    return render(request, "store/vendor_success.html")





def product_detail(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    # increment views
    product.views_count += 1
    product.save(update_fields=['views_count'])

    cart = Cart(request)
    form = ReviewForm()
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']

    # handle review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart': cart,
        'form': form,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })



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
    cart = Cart(request)  # ✅ Define cart at the start

    if request.method == 'POST':
        form = OrderForm(request.POST)  # ✅ Pass request.POST, not just request
        if form.is_valid():
            total_price = 0

            # Calculate total price
            for item in cart:
                product = item['product']
                total_price += product.price * int(item['quantity'])

            # Create order
            order = form.save(commit=False)
            order.created_by = request.user
            order.paid_amount = total_price
            order.save()

            # Create order items
            for item in cart:
                product = item['product']
                quantity = int(item['quantity'])
                price = product.price * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=price,
                    quantity=quantity
                )

            # Clear cart after successful checkout
            cart.clear()

            return redirect('myaccount')
    else:
        form = OrderForm()

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'form': form
    })



from django.db.models import Q, F
from django.db.models.functions import Sqrt, Power

def search(request):
    query = request.GET.get('query', '')
    products = Products.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        status=Products.ACTIVE
    )

    # Annotate distance if user has a location
    user = request.user
    if user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.latitude:
        user_lat = user.userprofile.latitude
        user_lon = user.userprofile.longitude

        products = products.annotate(
            distance=Sqrt(
                Power(F('latitude') - user_lat, 2) +
                Power(F('longitude') - user_lon, 2)
            )
        ).order_by('distance')  # Closest products first

    return render(request, 'store/search.html', {'products': products, 'query': query})





@login_required
def my_store_order_detail(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'userprofile/my_store_order_detail.html', {'order': order})

