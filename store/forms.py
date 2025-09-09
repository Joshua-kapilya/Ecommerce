from django import forms
from .models import Products
from .models import Order



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('created_by', 'phone_number', 'area', 'total_cost', 'paid_amount', 'merchant_id' )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ('category', 'title', 'description', 'price', 'image')
        widgets = {
            'category': forms.Select(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-indigo-200 focus:border-indigo-300'
            }),
            'title': forms.TextInput(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-indigo-200 focus:border-indigo-300',
                'placeholder': 'Enter product title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-indigo-200 focus:border-indigo-300',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-indigo-200 focus:border-indigo-300',
                'placeholder': 'Enter price'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full mt-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }
