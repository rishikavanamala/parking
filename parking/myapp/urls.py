from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home),
    path('avaliable_slots/',views.avaliable_slots,name="avaliable_slots"),
    path('book_slot/<int:id>/',views.book_slot,name="book_slot"),
    path('filled-slots/', views.filled_slots, name='filled_slots'),
    path('total-slots/', views.total_slots, name='total_slots'),
    path('occupy_slot/',views.occupy_slot, name='occupy_slot'),
    path('release_slot/<int:slot_id>',views.release_slot,name='release_slot'),
    path('reserve_slot/',views.reserve_slot,name='reserve_slot'),
    path('reserve_form/<int:slot_id>/',views.reserve_form,name ='reserve_form'),
    path('download_pdf/<int:id>/',views.download_pdf,name="download_pdf"),
    path('send_receipt_email/<int:id>/', views.send_receipt_email, name='send_receipt_email'),
]
