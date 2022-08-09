from django.urls import path
from . import payment

urlpatterns = [
    path('[--your_url--]', payment.pay_callback, name="pay_callback"),
]
