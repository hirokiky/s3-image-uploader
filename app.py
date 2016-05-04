import base64
import binascii
from io import BytesIO
import json
import os
from urllib.parse import unquote_plus
import uuid

import boto3
from botocore.exceptions import ClientError
import imghdr
import falcon
from PIL import Image

BUCKET_NAME = os.environ.get("IMAGE_S3_UPLOADER_BUCKET")
IMAGE_HOST_TEMP = os.environ.get(
    "IMAGE_S3_UPLOADER_LINK_TEMPLATE",
    "https://{bucket}.s3-ap-northeast-1.amazonaws.com/{key}"
)

ENDPOINT_SHOUOLD_BASICAUTH = os.environ.get("IMAGE_S3_UPLOADER_BASICAUTH") == "1"
ENDPOINT_USER = os.environ.get("IMAGE_S3_UPLOADER_USER")
ENDPOINT_PASSWORD = os.environ.get("IMAGE_S3_UPLOADER_PASSWORD")

assert BUCKET_NAME, "Environment Valiable IMAGE_S3_UPLOADER_BUCKET is required, see the README"

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)


def extract_basicauth(authorization_header, encoding='utf-8'):
    if not authorization_header:
        return None

    splitted = authorization_header.split(' ')
    if len(splitted) != 2:
        return None

    auth_type, auth_string = splitted

    if 'basic' != auth_type.lower():
        return None

    try:
        b64_decoded = base64.b64decode(auth_string)
    except (TypeError, binascii.Error):
        return None
    try:
        auth_string_decoded = b64_decoded.decode(encoding)
    except UnicodeDecodeError:
        return None

    splitted = auth_string_decoded.split(':')

    if len(splitted) != 2:
        return None

    username, password = map(unquote_plus, splitted)
    return username, password


def check_basic_credentials(credentials):
    r = extract_basicauth(credentials)
    if r is None:
        return False
    user, passwd = r
    return user == ENDPOINT_USER and passwd == ENDPOINT_PASSWORD


def upload_to_s3(image_b):
    mimetype = imghdr.what(BytesIO(image_b))
    key = str(uuid.uuid4()) + '.' + mimetype
    obj = bucket.Object(key)
    obj.put(
        Body=image_b,
        ContentType='image/' + mimetype,
    )
    return key


def make_url(key):
    return IMAGE_HOST_TEMP.format(bucket=BUCKET_NAME, key=key)


class ImagesResource:
    def on_post(self, req, resp):
        if ENDPOINT_SHOUOLD_BASICAUTH and not check_basic_credentials(req.auth):
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({
                'error': "Invalid credentials"
            })
            return
        b = req.stream.read()
        try:
            Image.open(BytesIO(b))
        except OSError:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({
                'error': 'Broken image',
            })
            return
        try:
            key = upload_to_s3(b)
        except ClientError:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({
                'error': "Internal server error",
            })
            return

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'image': make_url(key),
        })


app = falcon.API()
images = ImagesResource()

app.add_route('/', images)
