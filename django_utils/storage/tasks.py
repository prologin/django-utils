import logging
import os

from botocore.exceptions import ClientError
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand
from django.db.models.fields.files import FileField
from django.utils.module_loading import import_string

_logger = logging.getLogger(__name__)


@shared_task()
def clear_unreferenced_files(*args, **kwargs):
    """
    A celery task running periodically, which fetch all the unreferenced
    files in the S3 storage and delete them.
    """
    _logger.debug("Starting unreferenced files clearing")

    all_files = _get_all_files()
    static_files = _get_static_files()
    files_to_keep = _get_files_to_keep()

    files_to_delete = all_files - static_files - files_to_keep

    storage = import_string(settings.DEFAULT_FILE_STORAGE)()
    deleted_files = set()

    for file in files_to_delete:
        try:
            storage.bucket.Object(file).delete()
            deleted_files.add(file)
        except ClientError as err:
            # If the deletion fails with 404, the file is already deleted
            if err.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
                continue
            raise err from err

    if deleted_files:
        _logger.info(f"Files deleted: {' '.join(deleted_files)}")
    _logger.info(f"{len(deleted_files)} files deleted")


def _get_files_to_keep():
    _logger.debug("Getting files to keep")
    files_to_keep = set()

    for model in apps.get_models():
        file_fields = []

        # Find all file fields in the model
        for field in model._meta.get_fields():
            if isinstance(field, FileField):
                file_fields.append(field)

        # Find all files of model's objects
        for object in model.objects.all():
            for field in file_fields:
                field_instance = object.__getattribute__(field.attname)
                if not field_instance:
                    continue
                floc = field_instance.storage.location
                fname = field_instance.name
                file_path = os.path.join(floc, fname)
                files_to_keep.add(file_path)

    return files_to_keep


def _get_all_files():
    _logger.debug("Getting all the stored files")
    all_files = set()

    storages = [
        import_string(storage)()
        for storage in (
            settings.DEFAULT_FILE_STORAGE,
            settings.PRIVATE_FILE_STORAGE,
        )
    ]

    for storage in storages:
        paginator = storage.connection.meta.client.get_paginator(
            "list_objects"
        )
        pages = paginator.paginate(Bucket=storage.bucket_name)
        for page in pages:
            for entry in page.get("Contents", ()):
                all_files.add(entry["Key"])

    return all_files


def _get_static_files():
    _logger.debug("Getting static files")

    def get_files(storage, current_dir):
        filenames = set()
        dirs, files = storage.listdir(current_dir)
        filenames |= {
            os.path.join(storage.location, current_dir, file) for file in files
        }

        for dir in dirs:
            filenames |= get_files(storage, os.path.join(current_dir, dir))
        return filenames

    return get_files(staticfiles_storage, "")
