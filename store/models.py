from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from io import BytesIO
from django.utils import timezone

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
	quantity=models.IntegerField(blank=True, null=True)
	image = models.ImageField(upload_to='uploads/product_images/', blank=True, null=True)
	thumbnail = models.ImageField(upload_to='uploads/product_images/thumbnail/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=60, choices=STATUS_CHOICES, default=ACTIVE)
	is_sponsored = models.BooleanField(default=False)
	sold_count = models.PositiveIntegerField(default=0)
	views_count = models.PositiveIntegerField(default=0)

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



class Review(models.Model):
    product = models.ForeignKey('Products', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # one review per user per product

    def __str__(self):
        return f'{self.user.username} - {self.product.title} ({self.rating})'







class Order(models.Model):
	created_by = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	phone_number = models.CharField(max_length=15)
	area = models.CharField(max_length=20)
	total_cost = models.IntegerField(default=0)
	paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	merchant_id = models.CharField(max_length=255)
	total_price = models.IntegerField(null=True)
	PAYMENT_METHODS = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
	
	payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
	is_paid = models.BooleanField(default=False, null=True)
	payment_reference = models.CharField(max_length=100, null=True, blank=True)
	paid_at = models.DateTimeField(null=True, blank=True)
	
	def get_total_price(self):
		return self.price / 100



class OrderItem(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, related_name='items', on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)

    # New field for tracking vendor updates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)

    def confirm_received(self):
        """Mark item as received if it has been delivered."""
        if self.status == 'delivered' and not self.received:
            self.received = True
            self.received_at = timezone.now()
            self.save()

    def get_total_price(self):
        # Assuming price is stored in cents
        return (self.price * self.quantity) / 100

    def __str__(self):
        return f"{self.product.title} x {self.quantity} ({self.get_status_display()})"



class Store(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="store")
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="store_images/", blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    is_approved = models.BooleanField(default=False)  # ✅ new field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

