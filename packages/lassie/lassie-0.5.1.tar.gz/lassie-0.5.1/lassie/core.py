# -*- coding: utf-8 -*-

"""
lassie.core
~~~~~~~~~~~

This module contains a Lassie object to maintain settings across lassie.

"""

from os.path import basename

from bs4 import BeautifulSoup
import requests

from .compat import urljoin, urlparse
from .exceptions import LassieError
from .filters import FILTER_MAPS
from .utils import clean_text, convert_to_int, normalize_locale


REQUEST_OPTS = {
    'client': ('cert', 'headers', 'hooks', 'max_redirects', 'proxies'),
    'request': ('timeout', 'allow_redirects', 'stream', 'verify'),
}

IMAGE_MIMETYPES = [
    'image/jpeg', 'image/gif', 'image/bmp', 'image/png'
]


def merge_settings(fetch_setting, class_setting):
    """Merge settings for ``fetch``, method params have priority."""
    if fetch_setting is None:
        return class_setting

    if class_setting is None:
        return fetch_setting

    return fetch_setting


class Lassie(object):
    __attrs__ = [
        'open_graph', 'twitter_card', 'touch_icon', 'favicon',
        'all_images', 'parser', '_retrieve_content', 'client'
    ]

    def __init__(self):
        """Instantiates an instance of Lassie."""
        self.open_graph = True
        self.twitter_card = True
        self.touch_icon = True
        self.favicon = True
        self.all_images = False
        self.parser = 'html5lib'
        self.handle_file_content = False
        self._request_opts = {}
        self.client = requests.Session()

    @property
    def request_opts(self):
        return self._request_opts

    @request_opts.setter
    def request_opts(self, _dict):
        for k, v in _dict.items():
            if (k in REQUEST_OPTS['client'] or k in REQUEST_OPTS['request']):
                self._request_opts[k] = v
            if k in REQUEST_OPTS['client']:
                setattr(self.client, k, v)


    def __repr__(self):
        return '<Lassie [parser: %s]>' % (self.parser)

    def fetch(self, url, open_graph=None, twitter_card=None, touch_icon=None,
              favicon=None, all_images=None, parser=None, handle_file_content=None):
        """Retrieves content from the specified url, parses it, and returns
        a beautifully crafted dictionary of important information about that
        web page.

        Priority tree is as follows:
            1. Open Graph
            2. Twitter Card
            3. Other meta content (i.e. description, keywords)

        :param url: URL to send a GET request to
        :param open_graph: (optional) If ``True``, filters web page content for Open Graph meta tags. The content of these properties have top priority on return values.
        :type open_graph: bool
        :param twitter_card: (optional) If ``True``, filters web page content for Twitter Card meta tags
        :type twitter_card: bool
        :param touch_icon: (optional) If ``True``, retrieves Apple touch icons and includes them in the response ``images`` array
        :type touch_icon: bool
        :param favicon: (optional) If ``True``, retrieves any favicon images and includes them in the response ``images`` array
        :type favicon: bool
        :param all_images: (optional) If ``True``, retrieves images inside web pages body and includes them in the response ``images`` array. Default: False
        :type all_images: bool
        :param parser: (optional) String reference for the parser that BeautifulSoup will use
        :type parser: string
        :param handle_file_content: (optional) If ``True``, lassie will return a generic response when a file is fetched. Default: False
        :type handle_file_content: bool

        """

        # Set params, method params have priority over class params
        open_graph = merge_settings(open_graph, self.open_graph)
        twitter_card = merge_settings(twitter_card, self.twitter_card)
        touch_icon = merge_settings(touch_icon, self.touch_icon)
        favicon = merge_settings(favicon, self.favicon)
        all_images = merge_settings(all_images, self.all_images)
        parser = merge_settings(parser, self.parser)
        handle_file_content = merge_settings(handle_file_content, self.handle_file_content)

        data = {
            'images': [],
            'videos': [],
        }

        has_file_content = False
        content_type = None
        if handle_file_content:
            headers = self._retrieve_headers(url)
            content_type = headers.get('Content-Type')
            has_file_content = content_type and not 'text/html' in content_type

        if has_file_content and content_type:
            has_image_content = content_type in IMAGE_MIMETYPES
            if has_image_content:
                parsed_url = urlparse(url)
                data['title'] = basename(parsed_url.path.lstrip('/'))  # TODO: if the url doesn't have an extension, maybe we should match it up to the mimetype and append an ext?
                data['url'] = url
                data['images'].append({
                    'type': 'body_image',
                    'src': url,
                })
        else:
            html = self._retrieve_content(url)
            if not html:
                raise LassieError('There was no content to parse.')

            soup = BeautifulSoup(clean_text(html), parser)

            if open_graph:
                data.update(self._filter_meta_data('open_graph', soup, data, url))

            if twitter_card:
                data.update(self._filter_meta_data('twitter_card', soup, data))

            data.update(self._filter_meta_data('generic', soup, data))

            if touch_icon:
                data.update(self._filter_link_tag_data('touch_icon', soup, data, url))

            if favicon:
                data.update(self._filter_link_tag_data('favicon', soup, data, url))

            if all_images:
                # Maybe filter out 1x1, no "good" way to do this if image doesn't supply width/height
                data.update(self._find_all_images(soup, data, url))

            # TODO: Find a good place for setting url, title and locale
            lang = soup.html.get('lang') if soup.html.get('lang') else soup.html.get('xml:lang')
            if lang and (not 'locale' in data):
                locale = normalize_locale(lang)
                if locale:
                    data['locale'] = locale

            if not 'url' in data:
                data['url'] = url

            if not 'title' in data and hasattr(soup.title, 'string'):
                data['title'] = soup.title.string

        return data

    def _retrieve_headers(self, url):  # pragma: no cover
        request_kwargs = {}
        for k, v in self._request_opts.items():
            if k in REQUEST_OPTS['request']:
                # Set request specific kwarg
                request_kwargs[k] = v

        response = self.client.head(url, **request_kwargs)

        return response.headers

    def _retrieve_content(self, url):  # pragma: no cover
        try:
            request_kwargs = {}
            for k, v in self._request_opts.items():
                if k in REQUEST_OPTS['request']:
                    # Set request specific kwarg
                    request_kwargs[k] = v

            response = self.client.get(url, **request_kwargs)
        except requests.exceptions.RequestException as e:
            raise LassieError(e)

        return response.text

    def _filter_meta_data(self, source, soup, data, url=None):
        """This method filters the web page content for meta tags that match patterns given in the ``FILTER_MAPS``

        :param source: The key of the meta dictionary in ``FILTER_MAPS['meta']``
        :type source: string
        :param soup: BeautifulSoup instance to find meta tags
        :type soup: instance
        :param data: The response dictionary to manipulate
        :type data: (dict)

        """
        meta = FILTER_MAPS['meta'][source]
        meta_map = meta['map']

        html = soup.find_all('meta', {meta['key']: meta['pattern']})

        image = {}
        video = {}

        for line in html:
            prop = line.get(meta['key'])
            value = line.get('content')

            if prop in meta_map and not meta_map[prop] in data:
                # this could be bad in cases where any values that the property
                # is mapped up to (i.e. "src", "type", etc) are found in ``data``
                # TODO: Figure out a smoother way to prevent conflicts ^^^^^^^^
                image_prop = meta['image_key']
                video_prop = meta['video_key']

                if prop.startswith((image_prop, video_prop)) and \
                prop.endswith(('width', 'height')):
                    if prop.endswith(('width', 'height')):
                        value = convert_to_int(value)

                if meta_map[prop] == 'locale':
                    locale = normalize_locale(value)
                    if locale:
                        data['locale'] = locale

                if prop == 'keywords':
                    value = [v.strip() for v in value.split(',')]

                if image_prop and prop.startswith(image_prop) and value:
                    # og:image URLs can be relative
                    if prop == 'og:image' and url:
                        value = urljoin(url, value)
                    image[meta_map[prop]] = value
                elif video_prop and prop.startswith(video_prop) and value:
                    video[meta_map[prop]] = value
                else:
                    data[meta_map[prop]] = value

        if image:
            image['type'] = image_prop
            data['images'].append(image)
        if video:
            data['videos'].append(video)

        return data

    def _filter_link_tag_data(self, source, soup, data, url):
        """This method filters the web page content for link tags that match patterns given in the ``FILTER_MAPS``

        :param source: The key of the meta dictionary in ``FILTER_MAPS['link']``
        :type source: string
        :param soup: BeautifulSoup instance to find meta tags
        :type soup: instance
        :param data: The response dictionary to manipulate
        :type data: (dict)
        :param url: URL used for making an absolute url
        :type url: string

        """
        link = FILTER_MAPS['link'][source]

        html = soup.find_all('link', {link['key']: link['pattern']})

        for line in html:
            data['images'].append({
                'src': urljoin(url, line.get('href')),
                'type': link['type'],
            })

        return data

    def _find_all_images(self, soup, data, url):
        """This method finds all images in the web page content

        :param soup: BeautifulSoup instance to find meta tags
        :type soup: instance
        :param data: The response dictionary to manipulate
        :type data: (dict)

        """
        all_images = soup.findAll('img')
        for image in all_images:
            # Create image list then remove duplicate images?
            img = {
                'src': urljoin(url, image.get('src')),
                'alt': image.get('alt', ''),
                'type': u'body_image',
            }

            # Only include width and height if included as an attribute of the element
            width = convert_to_int(image.get('width'))
            if width:
                img['width'] = width

            height = convert_to_int(image.get('height'))
            if height:
                img['height'] = height

            data['images'].append(img)

        return data
