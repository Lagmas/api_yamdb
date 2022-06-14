from django.urls import include, path
from rest_framework import routers
from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet
                    )
from api.views import (
    CustomTokenObtainPairView,
)


router = routers.DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

app_name = 'api'

auth_endpoints = [
    path('v1/', include(router.urls)),
    path(
        'token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
]
