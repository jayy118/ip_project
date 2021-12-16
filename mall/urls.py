from django.urls import path
from . import views

urlpatterns = [
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('<int:pk>/', views.ProductDetail.as_view()),
    path('', views.ProductList.as_view()),
    path('category/<str:slug>/', views.category_page)
]