from django.db import models
from django.contrib.auth.models import User
import os
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name if self.name else f"Customer {self.id}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    digital = models.BooleanField(default=False,null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    main_image = models.ForeignKey(
        'ProductImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='main_image_for',
        verbose_name=_("Головне зображення")
    )

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name=_("Товар"))
    image = models.ImageField(null=True, blank=True, verbose_name=_("Зображення"))

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'name') and self.product and self.product.name:
            current_prefix = f"{self.product.name.replace(' ', '_')}_"
            if not os.path.basename(self.image.name).startswith(current_prefix):
                image_count = self.product.images.count()
                if self.pk is None:
                    image_count += 1

                filename, extension = os.path.splitext(self.image.name)
                safe_product_name = "".join(c if c.isalnum() else "_" for c in self.product.name)
                self.image.name = f"{safe_product_name}_{image_count}{extension}"
        super().save(*args, **kwargs)

    def __str__(self):
        if self.product and self.product.name:
            try:
                image_list = list(self.product.images.all().order_by('id'))
                image_count = image_list.index(self) + 1
                return f"{self.product.name} - Image {image_count}"
            except ValueError:
                 return f"{self.product.name} - Image (unsaved or detached)"
        return _("Зображення товару")


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = 'NEW', _('Нове')
        PROCESSING = 'PROC', _('В обробці')
        SHIPPED = 'SHIP', _('Відправлено')
        DELIVERED = 'DLVD', _('Доставлено')
        COMPLETED = 'COMP', _('Завершено')
        CANCELLED = 'CANC', _('Скасовано')
        PAYMENT_PENDING = 'PEND', _('Очікує оплати')

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Клієнт"))
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата замовлення"))
    complete = models.BooleanField(default=False, verbose_name=_("Завершено (старе поле)"))
    transaction_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("ID транзакції"))
    monobank_invoice_id = models.CharField(max_length=100, null=True, blank=True, unique=True, verbose_name=_("Monobank Invoice ID"))
    status = models.CharField(
        max_length=4,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name=_('Статус замовлення')
    )

    def __str__(self):
        return f"Order {self.id} (Status: {self.get_status_display()}, Inv: {self.monobank_invoice_id or 'N/A'})"

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
            if hasattr(i.product, 'digital') and i.product.digital == False:
                shipping = True
        return shipping

    @property
    def is_truly_completed(self):
        return self.status == self.OrderStatus.COMPLETED

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name=_("Товар"))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name=_("Замовлення"))
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name=_("Кількість"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата додавання"))

    @property
    def get_total(self):
        if self.product and self.product.price is not None and self.quantity is not None:
            total = self.product.price * self.quantity
            return total
        return 0

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else _('Видалений товар')} for Order {self.order.id if self.order else 'N/A'}"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name=_("Клієнт"))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name=_("Замовлення"))
    phone = models.CharField(max_length=20, null=True, verbose_name=_("Телефон"))
    address = models.CharField(max_length=200, null=False, verbose_name=_("Адреса"))
    city = models.CharField(max_length=200, null=False, verbose_name=_("Місто"))
    state = models.CharField(max_length=200, null=False, verbose_name=_("Область/Штат"))
    zipcode = models.CharField(max_length=200, null=False, verbose_name=_("Поштовий індекс"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата додавання"))

    def __str__(self):
        return self.address if self.address else _("Адреса доставки")