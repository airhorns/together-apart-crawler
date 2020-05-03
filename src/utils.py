from urllib.parse import urlparse


def extract_domain(url):
    try:
        return urlparse(url).hostname
    except Exception as _e:
        return None
