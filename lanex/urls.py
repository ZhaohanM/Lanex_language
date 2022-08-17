from django.urls import path
from lanex import views

app_name = 'lanex'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('explore/', views.explore, name='explore'),
    path('languages/', views.languages, name='languages'),
    path('language/<slug:language_name_slug>/', views.show_language, name='show_language'),
    path('language/<slug:language_name_slug>/<slug:request_name_slug>', views.show_request, name='show_request'),
    path('language/<slug:language_name_slug>/<slug:request_name_slug>/accept', views.accept_request, name='accept_request'),
    path('language/<slug:language_name_slug>/<slug:request_name_slug>/accept_request', views.accept_request, name='accept_request'), #
    path('language/<slug:language_name_slug>/<slug:request_name_slug>/delete', views.delete_request, name='delete_request'),
    path('add_language/', views.add_language, name='add_language'),
    path('language/<slug:language_name_slug>/add_request/', views.add_language_request, name='add_language_request'),
    path('user/<slug:user_profile_slug>/', views.show_user, name='show_user'),
    path('user/<slug:user_profile_slug>/settings/', views.user_settings, name='user_settings'),
    path('user/<slug:user_profile_slug>/delete/', views.user_delete, name='user_delete'),
    path('add_request/', views.add_request, name='add_request'),
    path('search/', views.search, name='search'),
    path('privacy_policy/', views.privacy, name='privacy'),
    path('terms_of_service/', views.terms, name='terms'),
]
