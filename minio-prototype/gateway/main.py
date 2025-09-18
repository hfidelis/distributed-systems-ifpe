import os
import boto3
import urllib.parse

from pydantic import BaseModel
from botocore.client import Config

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'videos')

app = FastAPI(title='MinIO + FastAPI Gateway')

s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

def ensure_bucket():
    try:
        s3.head_bucket(Bucket=MINIO_BUCKET)
    except Exception:
        try:
            s3.create_bucket(Bucket=MINIO_BUCKET)
        except Exception as e:
            print('Could not create bucket:', e)

@app.on_event('startup')
def startup():
    ensure_bucket()

class PresignRequest(BaseModel):
    filename: str
    content_type: str = 'application/octet-stream'
    expires_in: int = 3600

@app.post('/presign')
def presign(req: PresignRequest):
    key = req.filename
    try:
        url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': key, 'ContentType': req.content_type},
            ExpiresIn=req.expires_in
        )
        return {'url': url, 'key': key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/list')
def list_objects():
    try:
        resp = s3.list_objects_v2(Bucket=MINIO_BUCKET)
        items = []
        for obj in resp.get('Contents', []):
            items.append({'key': obj['Key'], 'size': obj['Size'], 'last_modified': obj['LastModified'].isoformat()})
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/download/{key}')
def presigned_get(key: str, expires_in: int = 3600):
    try:
        key_decoded = urllib.parse.unquote(key)
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': key_decoded},
            ExpiresIn=expires_in
        )
        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/', response_class=FileResponse)
def root():
    return 'static/index.html'
