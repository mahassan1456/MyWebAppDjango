from django.urls import path

from medical import views


app_name = 'medical'

urlpatterns = [


    path('success/', view=views.success, name='success'),
    path('', view=views.landing, name="landing"),
    path('register/', views.register, name='register'),
    path('dashboard/', view=views.dashboard, name='dashboard'),
    path('createuser/<int:hospital_id>/', view=views.createuser, name='createuser'),
    path('login/', views.login, name="login"),
    path('products/', views.products, name="products"),
    path('logout/', views.logout, name="logout"),
    path('contactus/',views.contact_us, name='contactus'),
    path('landing/', views.landing, name='landing'),
    path('facilities/', views.reviewAccount, name='reviewaccount'),
    path('details/<int:id>/', views.details, name='details'),
    path('confirmhospital/<int:id>/', views.confirmhospital, name='confirmhospital'),
    
 
]