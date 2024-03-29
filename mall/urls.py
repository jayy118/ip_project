from django.urls import path
from . import views

urlpatterns = [
    path('search/<str:q>/', views.ProductSearch.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('<int:pk>/', views.ProductDetail.as_view()),
    path('', views.ProductList.as_view()),
    path('<int:pk>/new_comment/', views.new_comment),
    path('category/<str:slug>/', views.category_page),
    path('publisher/<str:slug>/', views.publisher_page),
]