from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('about/', views.about, name='about'),
    path('kinds/', views.kind_groups, name='kind_groups'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/submit/', views.submit_cart, name='submit_cart'),
    path('cart/list/', views.cart_list, name='cart_list'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
