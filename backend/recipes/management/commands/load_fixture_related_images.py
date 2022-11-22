import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        fixture_images_path = os.path.join(
            settings.BASE_DIR, '..', 'data', 'images'
        )

        media_images_path = os.path.join(
            settings.MEDIA_ROOT, 'recipes', 'images'
        )

        if os.path.exists(media_images_path):
            shutil.rmtree(media_images_path)

        shutil.copytree(fixture_images_path, media_images_path)
