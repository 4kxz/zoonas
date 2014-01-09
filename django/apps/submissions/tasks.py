import os

from celery import task
from django.conf import settings
from django.core import files

from misc import thumbler

@task()
def thumbnail_task(model, pk):
    """Takes the submission link, finds an image and generates
    a thumbnail, then assigns that thumbnail to the submission.
    """
    query = model.objects.filter(pk=pk)
    if query.exists():
        submission = query.get()
        try:
            path = '/tmp/{}.jpg'.format(pk)
            f = files.File(open(path, 'w+'))
            thumbler.get_thumbnail(f, settings.THUMBNAIL_SIZE, submission.link)
        except thumbler.ThumbnailError:
            submission.thumbnail = submission.zone.thumbnail
            submission.save(update_fields=['thumbnail'])
        else:
            submission.thumbnail = f
            submission.save(update_fields=['thumbnail'])  # django-storages takes care of uploading
        finally:
            os.remove(path)
