import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import s3_client
from app.crud import delivery_photo as crud_photo
from app.enums import UserRole
from app.models.user import User
from app.services.route_service import route_service

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


class DeliveryPhotoService:
    async def get_route_photos(self, db: AsyncSession, route_id: int):
        photos = await crud_photo.get_photos_by_route(db, route_id)
        result = []
        for photo in photos:
            url = await s3_client.get_presigned_url(photo.key)
            photo_dict = photo.model_dump()
            photo_dict["url"] = url
            result.append(photo_dict)
        return result

    async def upload_photo(
        self,
        db: AsyncSession,
        route_id: int,
        file: UploadFile,
        description: str | None,
        current_user: User,
    ):
        self._validate_file(file)

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, detail="File size exceeds 10 MB limit"
            )

        key = self._generate_key(route_id, file.filename)

        # Actually upload to S3
        await s3_client.upload_file(
            file_data=contents, key=key, content_type=file.content_type
        )

        photo = await crud_photo.create_photo(db, route_id, key, description)

        url = await s3_client.get_presigned_url(key)
        return {"key": photo.key, "url": url}

    async def delete_photo(
        self, db: AsyncSession, photo_id: int, current_user: User
    ):
        photo = await crud_photo.get_photo_by_id(db, photo_id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")

        route = await route_service.get_route_or_404(db, photo.route_id)

        if (
            current_user.role != UserRole.MANAGER
            and route.driver_id != current_user.id
        ):
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this photo"
            )

        await s3_client.delete_file(photo.key)

        await crud_photo.delete_photo(db, photo)
        return {"status": "deleted"}

    def _validate_file(self, file: UploadFile):
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: "
                f"{', '.join(ALLOWED_CONTENT_TYPES)}",
            )

    def _generate_key(self, route_id: int, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
        return f"delivery_photos/route_{route_id}/{uuid.uuid4()}.{ext}"


delivery_photo_service = DeliveryPhotoService()
