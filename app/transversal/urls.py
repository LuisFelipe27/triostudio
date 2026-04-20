from django.urls import path
from app.transversal import api
from rest_framework import routers


app_name = 'transversal'

router = routers.DefaultRouter()
router.register(r'users', api.UserCreateViewSet)

urlpatterns = [
    # path('', visit_dashboard, name='dashboard'),
]
