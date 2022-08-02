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
from captures.models import Record, Station
from rest_framework import routers, serializers, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from . import views
import logging
import datetime 

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

class StationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Station
        fields = [
            'id',
            'author',
            'code', 
            'location_gps_lat', 
            'location_gps_lon']

# ViewSets define the view behavior.
class RecordViewSet(viewsets.ModelViewSet):
    serializer_class = RecordSerializer
    queryset = Record.objects.all()

    def get_queryset(self):
        queryset = Record.objects.all() # self, request, *args, **kwargs)
        author = self.request.GET.get('author')
        processed = self.request.GET.get('processed')
        date_from = self.request.GET.get('date_from')
        date_until = self.request.GET.get('date_until')
        location_code = self.request.GET.get('location_code')
        logging.info(processed)
        logging.info(bool(processed))
        if author is not None:
            queryset = queryset.filter(author=author)
        if processed is not None:
            queryset = queryset.filter(processed=bool(int(processed)))
        if date_from is not None:
            date_from_ymd = [int(x) for x in date_from.split('-')]
            queryset = queryset.filter(timestamp_upload__gte=datetime.date(date_from_ymd[0], date_from_ymd[1], date_from_ymd[2]))
        if date_until is not None:
            date_until_ymd = [int(x) for x in date_until.split('-')]
            queryset = queryset.filter(timestamp_upload__lte=datetime.date(date_until_ymd[0], date_until_ymd[1], date_until_ymd[2]))
        if location_code is not None:
            queryset = queryset.filter(location_code=location_code)

        # queryset = queryset.filter(processed=False)
        return queryset


class RecordBatchPost(APIView):
    queryset = Record.objects.all()

    def post(self, request):
        serializer = RecordSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(True, status=201)
        return Response(serializer.errors, status=400)

class StationViewSet(viewsets.ModelViewSet):
    serializer_class = StationSerializer
    queryset = Station.objects.all()

    def get_queryset(self):
        queryset = Station.objects.all() # self, request, *args, **kwargs)
        author = self.request.GET.get('author')
        if author is not None:
            queryset = queryset.filter(author=author)

        return queryset

class StationBatchDelete(APIView):
    queryset = Station.objects.all()

    def get(self, request):
        queryset = Station.objects.all() # self, request, *args, **kwargs)
        author = request.GET.get('author')
        if author is None:
            return False
        queryset = queryset.filter(author=author)
        queryset.delete()
        return Response(status=200)

class StationBatchPost(APIView):
    queryset = Station.objects.all()

    def post(self, request):
        serializer = StationSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(True, status=201)
        return Response(serializer.errors, status=400)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'records', RecordViewSet)
router.register(r'stations', StationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('sign_s3', views.sign_s3),
    path('load_pic', views.load_pic),
    path('unload_pic', views.unload_pic),
    path('process', views.process),
    path('api-auth/', include('rest_framework.urls')),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('session/', views.session_view, name='session'),
    path('whoami/', views.whoami_view, name='whoami'),
    path('get_csrf_token/', views.get_csrf, name='get_csrf_token'),
    path('station_batch_delete/', StationBatchDelete.as_view(), name='station_batch_delete'),
    path('station_batch_post/', StationBatchPost.as_view(), name='station_batch_post'),
    path('record_batch_post/', RecordBatchPost.as_view(), name='record_batch_post'),
]
