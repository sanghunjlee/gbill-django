from django.urls import path

from . import views

app_name = 'gbill'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('add/<int:bill_id>/', views.add, name='add'),
    path('bills/<int:pk>/', views.BillView.as_view(), name='detail'),
    path('bills/add/', views.BillCreateView.as_view(), name='bill_add'),
    # path('bills/<int:pk>/update/', views.BillUpdateView.as_view(), name='bill-update'),
    path('bills/delete/<int:pk>/', views.delete_bill, name='bill_delete'),
    path('bills/clear/', views.clear_bills, name='bill_clear'),
    path('person/<int:pk>', views.PersonView.as_view(), name='person'),
    path('person/add/', views.PersonAddView.as_view(), name='person_add'),
    path('person/delete/<int:pk>/', views.delete_person, name='person_delete'),
    path('person/clear/', views.clear_persons, name='person_clear')

]