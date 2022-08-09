from django.db import models


class LiqPayConfig(models.Model):
    """
    Settings for LiqPay system
    
    :param provider_token: - replace [--Token for Telegram pay--] to your token from @BotFather
    :param public_key:     - replace [--Public key LiqPay--] to your public key from LiqPay
    :param private_key:    - replace [--Private key LiqPay--] to your private key from LiqPay
    :param result_url:     - replace [--URL for redirect after payment in LiqPay--] to the link to which you plan to transfer the user after successful payment in LiqPay
    :param server_url:     - replace [--URL to get status from Liqpay--] to your callback link
    :param tax_percent:    - replace [--Commission--] to your tax percent
    :param is_active:      - [True] is active, [False} is inactive payment method
    
    """

    title = models.CharField('Title of config', max_length=80, default='Base config LiqPay')

    provider_token = models.CharField('[--Token for Telegram pay--]', max_length=200)
    public_key = models.CharField('[--Public key LiqPay--]', max_length=100)
    private_key = models.CharField('[--Private key LiqPay--]', max_length=100)

    result_url = models.CharField('[--URL for redirect after payment in LiqPay--]', max_length=200, default='', help_text="[--https://t.me/your_bot--]")
    server_url = models.CharField('[--URL to get status from Liqpay--]', max_length=200, default='', help_text="[--https://your_server_url.com--]")

    tax_percent = models.PositiveSmallIntegerField('[--Commission--]', default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    """Model to showcase a payment application"""
    name = models.CharField('[--Product name--]', max_length=200, default='')
    description = models.CharField('[--Product description--]', max_length=200, default='')
    img_url = models.CharField('[--URL for product picture--]', max_length=200, default='')
    price = models.CharField('[--Price--]', max_length=200, default='')
    currency = models.CharField('[--Currency--]', max_length=200, default='USD')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
