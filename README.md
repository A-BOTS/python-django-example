# Payment  
#### _Payment application for telegram bot in basic Django configuration_  
![N|Solid](https://alpha-bots.com/wp-content/uploads/2022/07/new_logo-1-2048x2013.png)

### Required dependencies:
`pyTelegramBotAPI==3.7.3`  
`Django==3.1.3`  
`liqpay-sdk-python3==1.0.3`  

_Also, for the application to work with messages, the `TBot` class of the `tbot` application of the same name from the base configuration is required._

### Application registration
1. Add the _payment_ application folder to your project folder
2. In the project's key directory:
   - in settings.py add the application name to the `INSTALLED_APPS` list - `"payment"`
   - in urls.py add to `urlpatterns` list `path("", include("payment.urls"))`

### Handlers
Add the following telegram handlers to the file to the rest (most often this is _/tbot/views.py_):
```python
from payment.payment import PaymentBot  # Import the class responsible for payments
from .models import Product

pBot = PaymentBot()  # Create an instance of this class


@tBot.bot.message_handler(func=lambda message: message.text and "Time Machine" in message.text)
def send_invoice_h(message):
	product = Product.objects.get(name="Time machine (used)")
	pBot.send_product_invoice(chat_id=message.from_user.id, message_id=message.message_id, product=product, user_lang="ru")


@tBot.bot.pre_checkout_query_handler(func=lambda pre_checkout_query: True)
def pre_checkout(pre_checkout_query):
	"""Responds to a request for pre-inspection"""
	tBot.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@tBot.bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
	"""Responds to a request for final payment confirmation"""
	product_name, product_photo_url, product_id, user_lang = message.successful_payment.invoice_payload.split('#')
	product = Product.objects.get(pk=product_id)
	pBot.success_payment(chat_id=message.from_user.id, message_id=message.message_id-1, product=product, 
				amount=message.successful_payment.total_amount/100, currency=message.successful_payment.currency, user_lang=user_lang)
```

### LiqPay Config
- In the dialog with @BotFather enter `/mybots` and select the bot you want to add the payment option to --> 
- select section `Payments` --> 
- `LiqPay` --> 
- select `LiqPay Test` (for payment testing) or `LiqPay Live` (for production) --> 
- follow the instructions to get the necessary keys --> 
- add the received `Provider token`, `Public key` and `Private key` to the corresponding fields of LiqPay Config via the admin panel, and fill in the rest.

![image-1.png](./image-1.png "`Provider token`") ![image-2.png](./image-2.png "`Public key` и `Private key`")

**For more information about payments in Telegram, see [official documentation](https://core.telegram.org/bots/payments).**
