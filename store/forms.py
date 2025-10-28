from django import forms
from .models import Products
from .models import Order, Store, OrderItem, Review



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('created_by', 'phone_number', 'area', 'total_cost', 'paid_amount', 'merchant_id' )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ('category', 'title', 'description', 'price', 'quantity', 'image')  # Added 'quantity'
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
            'quantity': forms.NumberInput(attrs={  # New field
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-indigo-200 focus:border-indigo-300',
                'placeholder': 'Enter available quantity',
                'min': '0'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full mt-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }



class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description", "image", "phone_number", "email", "province", 'town', "website", "category"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.update({
                "class": "w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
            })


class OrderItemStatusForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['status']




class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 'max': 5, 'class': 'border rounded-md w-20 p-1'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3, 'placeholder': 'Write your review...', 'class': 'w-full border rounded-md p-2'
            }),
        }

