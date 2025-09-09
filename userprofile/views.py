from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Userprofile
from store.forms import ProductForm
from store.models import Products, Category, OrderItem, Order
# Create your views here.

def vendor_detail(request, pk):
	user = User.objects.get(pk=pk)
	products = user.products.filter(status=Products.ACTIVE)

	return render(request, 'userprofile/vendor_detail.html', { 'user': user, 'products': products })

@login_required
def add_product(request):
	if request.method == 'POST':

		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			product = form.save(commit=False)
			product.user = request.user
			product.save()
			messages.success(request, 'the product was added!')
			return redirect('mystore')
	else:
		form = ProductForm()
	return render(request, 'userprofile/add_product.html', { 'form': form, 'title': ' Add product'})


@login_required
def delete_product(request, pk):
	product = Products.objects.filter(user=request.user).get(pk=pk)
	product.status = product.DELETED
	product.save()
	messages.success(request, 'the product was deleted!')

	return redirect('mystore')




@login_required
def edit_product(request, pk):
	product = Products.objects.filter(user=request.user).get(pk=pk)

	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			form.save()

			messages.success(request, 'the product was changed!')

			return redirect('mystore')
	else:

		form = ProductForm(instance=product)

	return render(request, 'userprofile/add_product.html', {'form': form, 'title': 'Edit product', 'product': product})



@login_required
def myaccount(request):
 	return render(request, 'userprofile/myaccount.html')

@login_required
def mystore(request):
	products = request.user.products.exclude(status=Products.DELETED)
	order_items = OrderItem.objects.filter(product__user=request.user)

	return render(request, 'userprofile/mystore.html', {'products': products, 'order_items': order_items})


def signup(request):

	if request.method == 'POST':

		form = UserCreationForm(request.POST)


		if form.is_valid():
			user = form.save()

			login(request, user)

			userprofile = Userprofile.objects.create(user=user)

			return redirect('frontpage')

	else:

		form = UserCreationForm()

	return render(request, 'userprofile/signup.html', {'form': form})

