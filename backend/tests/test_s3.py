import aiohttp
import pytest
from fastapi import status

from app.core.config import settings
from app.core.s3 import s3_client


@pytest.mark.asyncio
async def test_s3_lifecycle():
    test_key = "test/lifecycle.txt"
    test_content = b"Integration test content"

    try:
        async with s3_client.get_client() as s3:
            try:
                await s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
            except Exception:
                await s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)

        await s3_client.upload_file(
            file_data=test_content, key=test_key, content_type="text/plain"
        )

        url = await s3_client.get_presigned_url(test_key)
        assert url is not None
        assert settings.S3_BUCKET_NAME in url

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                assert response.status == status.HTTP_200_OK
                content = await response.read()
                assert content == test_content

    finally:
        async with s3_client.get_client() as s3:
            try:
                await s3.delete_object(
                    Bucket=settings.S3_BUCKET_NAME, Key=test_key
                )
                await s3.delete_bucket(Bucket=settings.S3_BUCKET_NAME)
            except Exception:
                pass
