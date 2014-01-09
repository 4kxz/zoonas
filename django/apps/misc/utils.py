import re
import unicodedata

sign = lambda x : cmp(0, x)

def merge_query(request, query):
    get = request.GET.copy()
    for key, value in query.items():
        get[key] = value
    return request.path + '?' + get.urlencode()

def clean_slug(string):
    string = re.sub(r'\ +', ' ', string).strip()
    string = '-' if string == '' else string
    slug = unicode(string)
    slug = unicodedata.normalize('NFKD', slug).encode('ascii','ignore').lower()
    slug = re.sub(r'([^\w])+', ' ', slug).strip()
    slug = re.sub(r'\ +', '-', slug)
    slug = '-' if slug == '' else slug
    return string, slug

def attribute_string(dictionary):
    return ' '.join('{}="{}"'.format(k, v) for k, v in dictionary.items())
