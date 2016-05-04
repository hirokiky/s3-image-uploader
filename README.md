# Image S3 Uploader

An image uploader for S3.

* Uploading to S3
* Accepting popular image types (jpeg, png, gif, bmp, and so)
* Guessing MIME types

## Client Usage

Just post image bodies to `/`.

Response will be:

```
{
    "image": "https://bucket-name.../b3dea8e8-77db-4b9f-82ef-73bd1176f06e.jpeg"
}
```

Accepting jpeg, png, gif, bmp, and so on.
See http://pillow.readthedocs.io/en/3.2.x/handbook/image-file-formats.html

## Setting Up

### Envirement Variables

Required:

* `IMAGE_S3_UPLOADER_BUCKET`: Bucket name to upload images files

Optional:

* `IMAGE_S3_UPLOADER_LINK_TEMPLATE`: Set template string for returned URL. `{bucket}` and `{key}` variables can be used in the template.  The default value is `"https://{bucket}.s3-ap-northeast-1.amazonaws.com/{key}"`.
* `IMAGE_S3_UPLOADER_BASICAUTH`: Set `"1"` to enable basic auth. Disabled by default
* `IMAGE_S3_UPLOADER_USER`: Username for the basic auth
* `IMAGE_S3_UPLOADER_PASSWORD`: Password for the basic auth

### Install and Run

```
pip install -r requirements.txt
gunicorn app:app --conf=./gunicorn.conf.py
```

Depending on accepting image formats, it may require some external libraries http://pillow.readthedocs.io/en/3.2.x/installation.html#external-libraries.
