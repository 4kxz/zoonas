from cStringIO import StringIO
import json
import os
from traceback import format_exc
from urllib2 import urlopen
from urlparse import urlparse, parse_qs

from embedly import Embedly
from PIL import Image


MAX_FILE_SIZE = 10 * 1000 * 1000
FILE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')


class ThumbnailError(Exception):
    pass


def twitter(source):
    user_name = urlparse(source).path.split('/')[1]
    info_url = ('http://api.twitter.com/1/users/profile_image'
                '?screen_name={}&size=bigger').format(user_name)
    return info_url


def vimeo(source):
    vid_id = urlparse(source).path.split('/')[-1]
    info_url = 'http://vimeo.com/api/v2/video/{}.json'.format(vid_id)
    info_json = urlopen(info_url).read().decode('utf-8')
    info = json.loads(info_json)
    return info[0].get('thumbnail_small')


def youtube(source):
    vid_id = parse_qs(urlparse(source).query)['v'][0]
    return 'http://img.youtube.com/vi/{}/mqdefault.jpg'.format(vid_id)


def embedly(source):
    key = os.environ['ZOONAS_EMBEDLY_KEY']
    return Embedly(key).oembed(source).data.get('thumbnail_url')


def get_thumbnail_url(source):
    """Returns the url of an image."""
    urlp = urlparse(source)
    # Invalid URL
    if urlp.hostname is None:
        url = None
    # Image URL
    elif urlp.path.endswith(FILE_EXTENSIONS):
        url = source
    # Known sites
    elif 'vimeo.com' in urlp.hostname:
        url = vimeo(source)
    elif 'youtube.com' in urlp.hostname or 'youtu.be' in urlp.hostname:
        url = youtube(source)
    else:
        url = embedly(source)
    return url


def get_image(source):
    """Donwloads the image from source."""
    resp = urlopen(source)
    info = resp.info().getheaders('Content-Length')
    if len(info) == 1 and int(info[0]) <= MAX_FILE_SIZE:
        bytes = resp.read()
        string = StringIO(bytes)
        return Image.open(string).convert('RGB')
    else:
        return None


def resize_image(img, size):
    """Scales and/or crops image (when bigger) to specified width."""
    tw, th = size
    iw, ih = img.size
    scale = max(1. * tw / iw, 1. * th / ih)
    if scale < 1:
        iw, ih = int(iw * scale), int(ih * scale)
        img = img.resize((iw, ih), Image.ANTIALIAS)
    tw, th = min(tw, iw), min(th, ih)
    dw, dh = (iw - tw) / 2, (ih - th) / 2
    box = [dw, dh, tw + dw, th + dh]
    return img.crop(box)


def get_thumbnail(f, size, url):
    """Attempts to retrieve an image from the url and generate
    a thumbnail and save it to f.
    """
    url = get_thumbnail_url(url)
    if url is None:
        raise ThumbnailError("No thumbnail found.")
    img = get_image(url)
    if img is None:
        raise ThumbnailError("Couldn't download image.")
    resize_image(img, size).save(f, quality=75)
