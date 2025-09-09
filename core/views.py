from django.shortcuts import render
from store.models import Products

# Create your views here.

def frontpage(request):
	products = Products.objects.filter(status=Products.ACTIVE)[0:6]
	return render(request, 'core/frontpage.html', {'products': products})
