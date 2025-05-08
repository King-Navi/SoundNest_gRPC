import os
import tempfile
import grpc
from typing import Iterator, Optional
from concurrent import futures
from dependency_injector.wiring import Provider, inject

from user_photo import user_image_pb2 , user_image_pb2_grpc
from src.services.user_images_service import UserImageService

class UserImageController(user_image_pb2_grpc.UserImageServiceServicer):
    @inject
    def __init__(self, image_service: UserImageService = Provider["user_image_service"]):
        self.image_service = image_service

    def UploadImage(
        self,
        request: user_image_pb2.UploadImageRequest,# pylint: disable=E1101
        context: grpc.ServicerContext
    ) -> user_image_pb2.UploadImageRequest: # pylint: disable=E1101
        try:
            self.image_service.upload_image(
                id_user=request.user_id,
                image_bytes=request.image_data,
                extension=request.extension
            )

            return user_image_pb2.UploadImageResponse( # pylint: disable=E1101
                success=True,
                message="Image uploaded successfully"
            )
        except Exception as e:
            return user_image_pb2.UploadImageResponse( # pylint: disable=E1101
                success=False,
                message=f"Failed to upload image: {str(e)}"
            )
    def DownloadImage(
        self,
        request: user_image_pb2.DownloadImageRequest, # pylint: disable=E1101
        context: grpc.ServicerContext
    ) -> user_image_pb2.DownloadImageResponse: # pylint: disable=E1101
        try:
            photos = self.image_service.photo_repository.get_photos_by_user_id(request.user_id)

            if not photos:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("No image found for this user.")
                return user_image_pb2.DownloadImageResponse() # pylint: disable=E1101

            photo = photos[0]  

            image_data = self.image_service.image_manager.load_user_image(
                photo.fileName,
                photo.extension
            )

            return user_image_pb2.DownloadImageResponse( # pylint: disable=E1101
                image_data=image_data,
                extension=photo.extension
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving image: {str(e)}")
            return user_image_pb2.DownloadImageResponse() # pylint: disable=E1101
