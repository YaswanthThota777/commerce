from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/', views.listing_view, name='listing_view'),
    path('watchlist/', views.watchlist_view, name='watchlist_view'),
    path('categories/', views.categories_view, name='categories_view'),
    path('categories/<int:category_id>/', views.category_listings_view, name='category_listings_view'),

]
