import os
import oss2
from config import OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET

app_name = 'creator'
bucket_name = 'ai-cp'
upload_dir = app_name
base_url = 'https://oss-cn-shanghai.aliyuncs.com'
bucket_url = f'https://{bucket_name}.oss-cn-shanghai.aliyuncs.com'
auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, base_url, bucket_name)


def oss_upload(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        result = bucket.put_object(f'{upload_dir}/{filename}', f)
    url = f'{bucket_url}/{upload_dir}/{filename}'
    return url


def oss_listdir(prefix=app_name):
    filenames = []
    for item in oss2.ObjectIterator(bucket, prefix=prefix):
        filenames.append(item.key)
    return filenames


def oss_download(filename, savepath=None):
    assert savepath is not None, 'The savepath should not be None'
    key = f'{upload_dir}/{filename}'
    bucket.get_object_to_file(key, savepath)
