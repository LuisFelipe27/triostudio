from django.urls import path
from app.multi_tenant import views
from app.multi_tenant import api
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'tenant', api.TenantViewset)

app_name = 'multi_tenant'


urlpatterns = [
    path('', views.index, name='index'),
    path('modal/create-client/', views.modal_create_client, name='modal-create-client'),
]
