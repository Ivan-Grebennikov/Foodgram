from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import SubscriptionViewSet

app_name = 'users'

auth_patterns = [
    path('', include('djoser.urls.authtoken')),
]

user_list = UserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve',
})

users_patterns = [
    path('', user_list, name='user_list'),
    path('<int:id>/', user_detail, name='user_detail'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user_me'),
    path(
        'set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='set_password',
    )
]

router_subscription = DefaultRouter()

router_subscription.register(
    'users', SubscriptionViewSet, basename='subscriptions'
)


urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('users/', include(users_patterns)),
    path('', include(router_subscription.urls)),
]
