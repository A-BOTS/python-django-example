from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from telebot import types
from liqpay import LiqPay
from time import time
from loguru import logger

from .models import LiqPayConfig
from tbot.tbot import TBot  # Base class for working with messages
from .models import Product  # Just for example


@csrf_exempt
def pay_callback(request):
    """
    Processes a response from LiqPay
    
    """
    pBot = PaymentBot()
    settings = LiqPayConfig.objects.filter(is_active=True).last()
    lqp = LiqPay(settings.public_key, settings.private_key)

    data = request.POST.get('data')
    signature = request.POST.get('signature')
    my_signature = lqp.str_to_sign(settings.private_key + data + settings.private_key)
    response = lqp.decode_data_from_str(data)

    if my_signature == signature:
        chat_id, message_id, product_id, user_lang = response['info'].split('#')
        product = Product.objects.get(pk=product_id)

        pBot.success_payment(chat_id=chat_id, message_id=message_id, product=product,
                             amount=response['amount'], currency=response['currency'], user_lang=user_lang)
    else:
        logger.info(response)
    return HttpResponse(status=200)


class PaymentBot(TBot):
    """
    The class responsible for payment methods
    """
    def __init__(self):
        super().__init__()
        self.settings = LiqPayConfig.objects.filter(is_active=True).last()
        self.lqp = LiqPay(self.settings.public_key, self.settings.private_key)

    def send_product_invoice(self, chat_id, message_id, product, user_lang):
        """
        Sends invoice with two payment buttons - via Telegram and via LiqPay

        :param chat_id: ID of target private chat (or of user)
        :param message_id: Message ID inside this chat
        :param product: DB object (e.g. Product.objects.get(title='Time machine'))
        :param user_lang: User language code (ISO 639-1) (e.g. "en" or "ru")
        """
        total = float(product.price) * ((100 + float(self.settings.tax_percent))/100)
        prices = [types.LabeledPrice(label=product.name, amount=int(total*100))]
        order_id = f"{chat_id}#{int(time())}"
        description = f"{product.name}\n\n{product.description}"
        info = f"{chat_id}#{int(message_id)+1}#{product.pk}#{user_lang}"

        html = self.lqp.checkout_url({
            'action': 'pay',
            'version': '3',
            'amount': round(total, 2),
            'currency': product.currency,
            'language': user_lang,
            'description': description,
            'info': info,
            'order_id': order_id,
            'result_url': self.settings.result_url,
            'server_url': self.settings.server_url,
        })

        markup = types.InlineKeyboardMarkup(row_width=1)
        pay_tel_btn = types.InlineKeyboardButton("Pay via Telegram", pay=True)
        pay_lqp_btn = types.InlineKeyboardButton("Pay via LiqPay", url=html)
        markup.add(pay_tel_btn, pay_lqp_btn)

        self.bot.send_invoice(chat_id=chat_id, provider_token=self.settings.provider_token, currency=product.currency,
                              title=product.name, description=product.description, prices=prices,
                              photo_url=product.img_url, photo_size=512, photo_width=512, photo_height=512,
                              start_parameter='start_parameter', invoice_payload=info,
                              need_name=None, need_phone_number=None, need_email=None, need_shipping_address=None,
                              is_flexible=False, reply_markup=markup)

    def success_payment(self, chat_id, message_id, product, amount, currency, user_lang):
        """
        Replaces a message with a product to a message with a receipt

        :param chat_id: ID of target private chat (or of user)
        :param message_id: Message ID inside this chat
        :param product: DB object (e.g. Product.objects.get(title='Time machine'))
        :param amount: Cost of product
        :param currency: Currency (e.g. "USD")
        :param user_lang: User language code (ISO 639-1) (e.g. "en" or "ru")
        """
        text = "<b>{product.name}</b>\n\n{product.description}\n\n<code>Total:</code>  <b><i>{amount} {currency}</i></b>"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Successfully paid ✅", callback_data='foo'))

        self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        self.bot.send_photo(chat_id=chat_id, photo=product.img_url, caption=text, parse_mode='HTML', reply_markup=markup)

    def get_receipt(self, order_id):
        """Gets status of payment"""
        response = self.lqp.api("request", {
            "action": "status",
            "version": "3",
            "order_id": order_id
        })
        return response

    def send_receipt_to_mail(self, order_id, email):
        """Sends receipt to the client email"""
        response = self.lqp.api("request", {
            "action": "ticket",
            "version": "3",
            "order_id": order_id,
            "email": email
        })
        return response['result']  # 'ok'
