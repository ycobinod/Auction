from django.urls import path
from .import views


urlpatterns = [
    path("",views.index, name="index"),
    path('login',views.login_view,name='login'),
    path('register',views.register, name='register'),
    path('logout',views.logout_view,name='logout'),
    path('create_listing', views.create_listing, name='create_listing'),
    path("<int:listing_id>", views.active_listing, name="active_listing"),
    path("watchlist", views.watchlist, name="watchlist")

]