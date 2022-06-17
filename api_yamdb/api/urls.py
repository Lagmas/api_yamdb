from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    CustomTokenObtainPairView,
    CommentViewSet,
    ReviewViewSet,
    RegisterUserViewSet,
    UsersViewSet
)


app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

auth_endpoints = [
    path(
        'token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'signup/',
        RegisterUserViewSet.as_view({'post': 'create'})
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    )
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_endpoints))
]
