import os
import boto3 
import json

from django.shortcuts import render        
from django.http import HttpResponse

def sign_s3(request):    
    S3_BUCKET = os.environ.get('S3_BUCKET')

    file_name =  request.GET.get('file_name')
    file_type = "image/jpeg" # request.args.get('file_type')

    s3 = boto3.client('s3', config = Config(signature_version = 's3v4'))

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
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    }))  
