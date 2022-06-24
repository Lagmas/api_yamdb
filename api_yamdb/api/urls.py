from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    CustomTokenObtainPairView,
    CommentViewSet,
    ReviewViewSet,
)

from users.views import (
    RegisterUserViewSet,
    UsersViewSet,
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

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
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_endpoints))
]
