from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import hello_page, login_page, register_page, profile_page, model_history, model_generate_post


urlpatterns = [
    path('', hello_page, name="home"),
    path('account/login', login_page, name="login"),
    path('account/register', register_page, name="register"),
    path('account/logout', LogoutView.as_view(next_page='home'), name='logout'),
    # alpha
    path('account/profile', profile_page, name="profile"),

    path('model/generate_post', model_generate_post, name='generate_post'),
    path('model/history', model_history, name='history')
]
