from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Customer, Product, Order, OrderItem, ShippingAddress, ProductImage

class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    fields = ('customer', 'phone', 'address', 'city', 'state', 'zipcode')
    readonly_fields = ('customer',)
    extra = 0
    max_num = 1
    can_delete = True
    verbose_name = _("Адреса доставки для цього замовлення")
    verbose_name_plural = _("Адреса доставки для цього замовлення")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'get_item_total_display')
    readonly_fields = ('product', 'get_item_total_display',)
    extra = 0
    can_delete = False
    verbose_name = _("Товар у замовленні")
    verbose_name_plural = _("Товари в замовленні")

    def get_item_total_display(self, obj):
        return f"₴{obj.get_total:.2f}"
    get_item_total_display.short_description = _('Вартість позиції')

class OrderInline(admin.TabularInline):
    model = Order
    fields = ('order_link', 'date_ordered', 'status', 'get_cart_items', 'get_cart_total_display')
    readonly_fields = ('order_link', 'date_ordered', 'status', 'get_cart_items', 'get_cart_total_display')
    extra = 0
    ordering = ('-date_ordered',)
    can_delete = False
    verbose_name = _("Замовлення клієнта")
    verbose_name_plural = _("Замовлення клієнта")

    def get_cart_total_display(self, obj):
        return f"₴{obj.get_cart_total:.2f}"
    get_cart_total_display.short_description = _('Загальна сума замовлення')

    def order_link(self, obj):
        if obj.id:
            url = reverse('admin:shop_order_change', args=[obj.id])
            return format_html('<a href="{}">{} #{}</a>', url, _('Переглянути замовлення'), obj.id)
        return "N/A"
    order_link.short_description = _('Деталі замовлення')

    def has_add_permission(self, request, obj=None):
         return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'date_ordered', 'status', 'complete', 'get_cart_items_display', 'get_cart_total_display', 'monobank_invoice_id_link')
    list_filter = ('status', 'complete', 'date_ordered')
    search_fields = ('id', 'customer__name', 'customer__email', 'monobank_invoice_id')
    readonly_fields = ('date_ordered', 'transaction_id', 'customer', 'monobank_invoice_id')
    list_per_page = 25
    inlines = [OrderItemInline, ShippingAddressInline]

    fieldsets = (
        (None, {
            'fields': ('customer', 'date_ordered', 'status', 'complete')
        }),
        (_('Деталі оплати'), {
            'fields': ('transaction_id', 'monobank_invoice_id'),
        }),
    )
    
    def customer_link(self, obj):
        if obj.customer:
            url = reverse('admin:shop_customer_change', args=[obj.customer.id])
            return format_html('<a href="{}">{}</a>', url, obj.customer.name or obj.customer.email or _('Клієнт ') + str(obj.customer.id))
        return _("Гість")
    customer_link.short_description = _('Клієнт')

    def get_cart_total_display(self, obj):
        return f"₴{obj.get_cart_total:.2f}"
    get_cart_total_display.short_description = _('Загальна сума')

    def get_cart_items_display(self, obj):
        return obj.get_cart_items
    get_cart_items_display.short_description = _('К-сть товарів')

    def monobank_invoice_id_link(self,obj):
        if obj.monobank_invoice_id and obj.monobank_invoice_id.startswith('inv_'):
            url = f"https://api.monobank.ua/some/path/to/invoice/{obj.monobank_invoice_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.monobank_invoice_id)
        return obj.monobank_invoice_id
    monobank_invoice_id_link.short_description = _('Monobank Invoice ID')


@admin.register(Customer)
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
        return _("Гість (не зареєстрований)")
    user_link.short_description = _('Обліковий запис користувача')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_thumbnail',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return ""
    image_thumbnail.short_description = _('Мініатюра')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'digital', 'main_image_display')
    search_fields = ('name',)
    fields = ('name', 'price', 'digital', 'description', 'image', 'main_image')
    inlines = [ProductImageInline]

    def main_image_display(self, obj):
        if obj.main_image and obj.main_image.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.main_image.image.url)
        elif obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return _("Немає зображення")
    main_image_display.short_description = _('Головне зображення')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "main_image":
            product_id = request.resolver_match.kwargs.get('object_id')
            if product_id:
                kwargs["queryset"] = ProductImage.objects.filter(product_id=product_id)
            else:
                kwargs["queryset"] = ProductImage.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


if not admin.site.is_registered(OrderItem):
    admin.site.register(OrderItem)

if not admin.site.is_registered(ShippingAddress):
    admin.site.register(ShippingAddress)

if not admin.site.is_registered(ProductImage):
    class ProductImageAdmin(admin.ModelAdmin):
        list_display = ('product', 'image_thumbnail_display', 'image')
        list_filter = ('product',)
        search_fields = ('product__name',)

        def image_thumbnail_display(self, obj):
            if obj.image:
                return format_html('<img src="{}" height="50px"/>', obj.image.url)
            return _("Немає зображення")
        image_thumbnail_display.short_description = _('Мініатюра')
    admin.site.register(ProductImage, ProductImageAdmin)

