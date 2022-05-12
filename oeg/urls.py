"""oeg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from captures.models import Record
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from . import views
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

# Serializers define the API representation.
class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = [
            'id',
            'uuid',
            'author',
            'processed',
            'location_code', 
            'location_gps_lat', 
            'location_gps_lon', 
            'front_pic_url', 
            'front_count', 
            'back_pic_url',
            'back_count', 
            'loc_pic_url',
            'happy', 
            'timestamp_upload',
            'timestamp_process']

# ViewSets define the view behavior.
class RecordViewSet(viewsets.ModelViewSet):
    serializer_class = RecordSerializer
    queryset = Record.objects.all()

    def get_queryset(self):
        queryset = Record.objects.all() # self, request, *args, **kwargs)
        author = self.request.GET.get('author')
        processed = self.request.GET.get('processed')
        logging.info(processed)
        logging.info(bool(processed))
        if author is not None:
            queryset = queryset.filter(author=author)
        if processed is not None:
            queryset = queryset.filter(processed=bool(int(processed)))
        # queryset = queryset.filter(processed=False)
        return queryset
    
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'records', RecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('sign_s3', views.sign_s3),
    path('load_pic', views.load_pic),
    path('unload_pic', views.unload_pic),
    path('process', views.process),
    path('api-auth/', include('rest_framework.urls')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('session/', views.session_view, name='session'),
    path('whoami/', views.whoami_view, name='whoami'),
    path('get_csrf_token/', views.get_csrf, name='get_csrf_token'),
]
