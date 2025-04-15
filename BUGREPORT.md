- не працює підтягунтий  css до html
  ✅ -- було створено STATICFILES_DIRS в settings.py
- не показує замовлення клієнта  [![](https://xxxx.rip/nenxmdng.png)](https://xxxx.rip/nenxmdng.png)
  ✅ -- оновлено шаблон cart.html, використовуючи коректний шлях до зображень item.product.imageURL
- не відображає фото товару
  [![](https://kun.xxxx.rip/iv4gf8og.png)](https://kun.xxxx.rip/iv4gf8og.png)
  ✅ -- оновлено шаблон cart.html, використовуючи коректний шлях до зображень item.product.imageURL
- не переходить на оплату
  [![](https://kun.xxxx.rip/09u58y7q.png)](https://kun.xxxx.rip/09u58y7q.png)
  ✅ -- додано CSRF-токен у checkout.html через {% csrf_token %}
- проведено тестування адмін-таблиці, підтягнули всю інфу під певний айді замовлення
- після оформлення замовлення кошик залишається, добре було би прибрати
  [![](https://xxxx.rip/uz54ls8o.png)](https://xxxx.rip/uz54ls8o.png)
  ✅ -- без паніки, додано `response.delete_cookie('cart', path='/')`
