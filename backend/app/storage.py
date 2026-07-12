import io, os, uuid
from minio import Minio

class OptionalArtifactStorage:
    def __init__(self):
        self.enabled = os.getenv("OBJECT_STORAGE_ENABLED", "false").lower() == "true"
        self.bucket = os.getenv("MINIO_BUCKET", "rentwise-artifacts")
        self.client = Minio(os.getenv("MINIO_ENDPOINT", "minio:9000"), access_key=os.getenv("MINIO_ACCESS_KEY", "rentwise"), secret_key=os.getenv("MINIO_SECRET_KEY", "change-me"), secure=os.getenv("MINIO_SECURE", "false").lower() == "true") if self.enabled else None
    def upload(self, user_id, filename: str, data: bytes, content_type: str, consent: bool) -> str:
        if not consent: raise ValueError("保存文件需要用户明确授权")
        if not self.enabled or not self.client: raise ValueError("对象存储未启用")
        if len(data) > 10 * 1024 * 1024: raise ValueError("单个授权文件不能超过 10MB")
        if not self.client.bucket_exists(self.bucket): self.client.make_bucket(self.bucket)
        key = f"{user_id}/{uuid.uuid4()}-{filename[:100]}"; self.client.put_object(self.bucket, key, io.BytesIO(data), len(data), content_type=content_type); return key
    def delete(self, user_id, key: str):
        if not self.enabled or not self.client or not key.startswith(f"{user_id}/"): raise ValueError("对象不存在或无权删除")
        self.client.remove_object(self.bucket, key)
