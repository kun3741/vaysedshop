
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Customer, Product, Order, OrderItem, ShippingAddress, ProductImage

class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    fields = ('customer', 'phone', 'address', 'city', 'state', 'zipcode')
    readonly_fields = ('customer',)
    extra = 0
    max_num = 1
    can_delete = True
    verbose_name = "Shipping Address for this Order"
    verbose_name_plural = "Shipping Address for this Order"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'get_item_total_display')
    readonly_fields = ('product', 'get_item_total_display',)
    extra = 0
    can_delete = False
    verbose_name = "Item in Order"
    verbose_name_plural = "Items in Order"

    def get_item_total_display(self, obj):
        return f"₴{obj.get_total:.2f}"
    get_item_total_display.short_description = 'Item Total'

class OrderInline(admin.TabularInline):
    model = Order
    fields = ('order_link', 'date_ordered', 'complete', 'get_cart_items', 'get_cart_total_display')
    readonly_fields = ('order_link', 'date_ordered', 'complete', 'get_cart_items', 'get_cart_total_display')
    extra = 0
    ordering = ('-date_ordered',)
    can_delete = False
    verbose_name = "Customer Order"
    verbose_name_plural = "Customer Orders"

    def get_cart_total_display(self, obj):
        return f"₴{obj.get_cart_total:.2f}"
    get_cart_total_display.short_description = 'Order Total'

    def order_link(self, obj):
        if obj.id:
            url = reverse('admin:shop_order_change', args=[obj.id])
            return format_html('<a href="{}">View Order #{}</a>', url, obj.id)
        return "N/A"
    order_link.short_description = 'Order Details'

    def has_add_permission(self, request, obj=None):
         return False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_ordered', 'complete', 'get_cart_items', 'get_cart_total_display', 'monobank_invoice_id')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('id', 'customer__name', 'customer__email', 'monobank_invoice_id')
    readonly_fields = ('date_ordered', 'transaction_id', 'monobank_invoice_id', 'customer')
    list_per_page = 25

    inlines = [ShippingAddressInline, OrderItemInline]

    def get_cart_total_display(self, obj):
        return f"₴{obj.get_cart_total:.2f}"
    get_cart_total_display.short_description = 'Total'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'user_link')
    search_fields = ('name', 'phone', 'email', 'user__username')
    list_filter = ('user',)
    readonly_fields = ('user',)
    inlines = [OrderInline]

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Guest"
    user_link.short_description = 'User Account'


class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 1

class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'price', 'digital', 'main_image')
	search_fields = ('name',)
	fields = ('name', 'price', 'digital', 'description', 'main_image')
	inlines = [ProductImageInline]


for model in [Customer, Order, Product, OrderItem, ShippingAddress, ProductImage]:
     try:
         admin.site.unregister(model)
     except admin.sites.NotRegistered:
         pass

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(ProductImage)