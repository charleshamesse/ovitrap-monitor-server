from concurrent.futures import thread
import os
import boto3 
from botocore.client import Config
import json
import glob
import logging
import cv2
import urllib.request
import numpy as np
# Get an instance of a logger
logger = logging.getLogger(__name__)
from django.shortcuts import render        
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from .egg_counter import EggCounter


# Egg counting
def load_pic(request):    

    pic_url =  str(request.GET.get('pic_url'))
    req = urllib.request.urlopen('http://oeg-pictures.s3.amazonaws.com/%s' % pic_url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    image = cv2.imdecode(arr, -1)


    eg = EggCounter()
    _, coords = eg.find_stick(image)


    if not os.path.exists("./ws"):
        os.makedirs("./ws")
    
    pic_url = pic_url.split('/')[-1]
    result = cv2.imwrite("./ws/%s" % pic_url, image)

    return HttpResponse(json.dumps({
        'pic_load': result,
        'coords': coords,
        'size': image.shape
    }))  

def process(request):    
    # load request arguments
    pic_url =  str(request.GET.get('pic_url'))
    pic_url = pic_url.split('/')[-1]
    threshold =  int(request.GET.get('threshold'))
    bbox = request.GET.get('bbox')

    # load counter and image
    eg = EggCounter()
    image = cv2.imread('./ws/%s' % pic_url)

    if bbox is not None:
        # if bbox is mentioned, skip finding the bbox
        top, left, height, width = [int(x) for x in bbox.split(',')]
        image_stick = image[top:top+height, left:left+width]
    else:  
        # else, find the bbox manually
        image_stick, _ = eg.find_stick(image)
    results = eg.count_eggs_single_thresh(image_stick, threshold)
    # plt.imshow(results['outlines'])
    # plt.show()

    return HttpResponse(json.dumps({
        'data': results,
    }))  

def unload_pic(request):
    pic_url =  str(request.GET.get('pic_url'))
    pic_url = pic_url.split('/')[-1]
    if os.path.exists("./ws/%s" % pic_url): res = os.remove("./ws/%s" % pic_url)
    else: res = "not found"
            
    return HttpResponse(json.dumps({
        'pic_unload': res
    }))  

# S3 upload
def sign_s3(request): 
    S3_BUCKET = os.environ.get('S3_BUCKET')
    if not S3_BUCKET:
        S3_BUCKET = 'oeg-pictures'
    print(S3_BUCKET)
    logging.info('s3_sign::S3_BUCKET' + S3_BUCKET)

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


# auth
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

@ensure_csrf_cookie
def register_view(request):

    data = json.loads(request.body)

    # create user
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if username is None or password is None or email is None:
        return JsonResponse({'detail': 'Please provide e-mail, username and password.'}, status=400)

    try:
        user = User.objects.create_user(username, email, password)
        # add basic permissions
        codenames_permissions = ['add_record',
            'change_record',
            'delete_record',
            'view_record',
            'add_capture',
            'change_capture',
            'delete_capture',
            'view_capture',
            'add_station',
            'change_station',
            'delete_station',
            'view_station']
        for codename in codenames_permissions:
            try:
                user.user_permissions.add(Permission.objects.get(codename=codename))
            except: 
                return JsonResponse({'detail': 'Error:' + codename}, status=400)
        user.save()
    except Exception as e:
        return JsonResponse({'detail': 'Error:' + e.__str__()}, status=400)



    # log in 
    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=400)

    login(request, user)
    return JsonResponse({'detail': 'Successfully registered and logged in.'})


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