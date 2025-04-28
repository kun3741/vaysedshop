from django.db import models
from django.contrib.auth.models import User
import os

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True, blank=True)
	phone = models.CharField(max_length=20, null=True)

	def __str__(self):
		return self.name
	
class Product(models.Model):
	name = models.CharField(max_length=200)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	main_image = models.ForeignKey(
		'ProductImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='main_image_for'
	)

	def __str__(self):
		return self.name

class ProductImage(models.Model):
	product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
	image = models.ImageField(null=True, blank=True)

	def save(self, *args, **kwargs):
		if self.image and not self.image.name.startswith(f"{self.product.name}_"):
			image_count = self.product.images.count() + 1
			extension = os.path.splitext(self.image.name)[1]
			self.image.name = f"{self.product.name}_{image_count}{extension}"
		super().save(*args, **kwargs)

	def __str__(self):
		image_count = list(self.product.images.all()).index(self) + 1
		return f"{self.product.name} - Image {image_count}"

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	monobank_invoice_id = models.CharField(max_length=100, null=True, blank=True, unique=True)

	def __str__(self):
		return f"Order {self.id} (Inv: {self.monobank_invoice_id or 'N/A'})"


	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 
	
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)
	
	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total


class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	phone = models.CharField(max_length=20, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
	