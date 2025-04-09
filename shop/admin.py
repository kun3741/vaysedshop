from django.contrib import admin

from .models import *

class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 1

class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'price', 'digital', 'main_image')
	search_fields = ('name',)
	fields = ('name', 'price', 'digital', 'description', 'main_image')
	inlines = [ProductImageInline]

admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(ProductImage)
