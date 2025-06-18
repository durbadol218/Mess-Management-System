from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate-payment'),
    path('success/', views.payment_success, name='payment-success'),
    path('fail/', views.payment_fail, name='payment-fail'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
    path('ipn/', views.payment_ipn, name='payment-ipn'),
    # path('payment-history/', views.payment_history, name='payment-history'),
]