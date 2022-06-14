from django.urls import path
from rest_framework import routers
from api.views import CommentViewSet, ReviewViewSet


from api.views import (
    CustomTokenObtainPairView,
)

app_name = 'api'

auth_endpoints = [
    path(
        'token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
]





router = routers.DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')