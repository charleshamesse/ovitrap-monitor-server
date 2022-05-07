import os
import boto3 
from botocore.client import Config
import json
import glob
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
from django.shortcuts import render        
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout

def sign_s3(request):    
    S3_BUCKET = os.environ.get('S3_BUCKET')

    file_name =  request.GET.get('file_name')
    file_type = "image/jpeg" # request.args.get('file_type')

    s3 = boto3.client('s3', config = Config(
        signature_version = 's3v4',
        region_name = 'sa-east-1',))

    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = { "acl": "public-read", "Content-Type": file_type},
        Conditions = [
            { "acl": "public-read" },
            { "Content-Type": file_type }
        ],
        ExpiresIn = 3600
    )
    return HttpResponse(json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/' % S3_BUCKET
    }))  



def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


@ensure_csrf_cookie
def login_view(request):

    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return JsonResponse({'detail': 'Please provide username and password.'}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=400)

    login(request, user)
    return JsonResponse({'detail': 'Successfully logged in.'})


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=400)

    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True})


def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'username': request.user.username})