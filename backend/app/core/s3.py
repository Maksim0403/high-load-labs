import logging

import aioboto3

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.bucket_name = settings.S3_BUCKET_NAME
        self.region = settings.S3_REGION

    def get_client(self):
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    async def upload_file(
        self, file_data: bytes, key: str, content_type: str = "image/jpeg"
    ):
        try:
            async with self.get_client() as s3:
                logger.info(
                    f"Uploading file to S3: "
                    f"bucket={self.bucket_name}, key={key}"
                )
                response = await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_data,
                    ContentType=content_type,
                )
                logger.info(f"S3 upload successful: {response}")
                return response
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise

    async def delete_file(self, key: str):
        try:
            async with self.get_client() as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=key)
                logger.info(f"S3 file deleted: {key}")
        except Exception as e:
            logger.error(f"S3 delete failed: {str(e)}")
            raise

    async def get_presigned_url(self, key: str, expires_in: int = 3600):
        async with self.get_client() as s3:
            return await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )


s3_client = S3Client()
