from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from io import BytesIO

from PIL import Image

# Create your models here.

class Category(models.Model):
	title = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50)


	class Meta:
		verbose_name_plural = 'Categories'


	def __str__(self):
		return self.title


class Products(models.Model):
	DRAFT = 'draft'
	WAITING_APPROVAL = 'waitingapproval'
	ACTIVE = 'active'
	DELETED = 'deleted'

	STATUS_CHOICES = (

		(DRAFT, 'draft'),
		(WAITING_APPROVAL, 'waiting approval'),
		(ACTIVE, 'active'),
		(DELETED, 'deleted')


		)

	user = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
	category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50)
	description = models.TextField(blank=True)
	price = models.IntegerField()
	image = models.ImageField(upload_to='uploads/product_images/', blank=True, null=True)
	thumbnail = models.ImageField(upload_to='uploads/product_images/thumbnail/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=60, choices=STATUS_CHOICES, default=ACTIVE)

	class Meta:
		ordering = ('-created_at',)



	def __str__(self):
		return self.title


	def get_display_price(self):
		return self.price / 100


	def get_thumbnail(self):
		if self.thumbnail:
			return self.thumbnail.url
		else:
			if self.image:
				self.thumbnail = self.make_thumbnail(self.image)
				self.save()
				return self.thumbnail.url
			else:
				return 'https://via.placeholder.com/240×240×.jpg'

	def make_thumbnail(self, image, size=(300, 300)):
		img = Image.open(image)
		img.convert('RGB')
		img.thumbnail(size)
		thumb_io = BytesIO()
		img.save(thumb_io, 'JPEG', quality=85)
		name = image.name.replace('uploads/product_images/', '')

		thumbnail = File(thumb_io, name=name)

		return thumbnail






class Order(models.Model):
	created_by = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	phone_number = models.CharField(max_length=15)
	area = models.CharField(max_length=20)
	total_cost = models.IntegerField(default=0)
	paid_amount = models.BooleanField(default=False)
	merchant_id = models.CharField(max_length=255)



class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Products, related_name='items', on_delete=models.CASCADE)
	price = models.IntegerField()
	quantity = models.IntegerField(default=1)

	def get_total_price(self):
		return self.price / 100