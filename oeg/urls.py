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
from captures.models import Capture
from rest_framework import routers, serializers, viewsets
from . import views

# Serializers define the API representation.
class CaptureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Capture
        fields = [
            'location_code', 
            'front_pic_url', 
            'front_count', 
            'back_pic_url',
            'back_count', 
            'happy', 
            'timestamp']
# ViewSets define the view behavior.
class CapturesViewSet(viewsets.ModelViewSet):
    queryset = Capture.objects.all()
    serializer_class = CaptureSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'captures', CapturesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('sign_s3', views.sign_s3),
    path('api-auth/', include('rest_framework.urls'))
]
