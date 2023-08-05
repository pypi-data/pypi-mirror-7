""":mod:`niconico_translator` --- Translating comments on Nico Nico Douga
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import locale
import logging
import optparse
import random
import re
import sys
import time

from dns.resolver import query
from lxml.html.html5parser import document_fromstring
from lxml.etree import fromstring, tostring
from requests import post, request
from waitress import serve
from webob import Request, Response
from webob.multidict import MultiDict

__all__ = 'App', 'main'


# We resolve the hostname of msg.nicovideo.jp using dnspython,
# to workaround the situation that msg.nicovideo.jp refers to 127.0.0.1
# in /etc/hosts file.
API_HOSTNAME = 'msg.nicovideo.jp'
API_IP_ADDRESS = query(API_HOSTNAME)[0].to_text()

HOPPISH_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
    'upgrade', 'content-encoding'
}


class App(object):
    """Proxy to msg.nicovideo.jp with translation."""

    def __init__(self, language):
        self.language = language

    def wsgi_app(self, environ, start_response):
        original_request = Request(environ)
        headers = MultiDict(original_request.headers)
        original_request.host = API_IP_ADDRESS
        original_response = request(
            original_request.method,
            original_request.url,
            headers=headers,
            data=original_request.body
        )
        response = Response()
        response.status = original_response.status_code
        response.headers = original_response.headers
        for hop in HOPPISH_HEADERS:
            response.headers.pop(hop, None)
        if has_to_translate(original_request, original_response):
            response.body = translate_response(
                original_response.content,
                self.language
            )
        else:
            response.body = original_response.content
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        try:
            return self.wsgi_app(environ, start_response)
        except Exception as e:
            logger = logging.getLogger(__name__ + '.App')
            logger.exception(e)
            raise


def has_to_translate(request, response):
    """Whether the response has to be translated or not."""
    return (request.method == 'POST' and
            response.headers.get('Content-Type') == 'text/xml')


def translate_response(xml, language):
    """Translate XML response."""
    document = fromstring(xml)
    chats = [chat for chat in document.xpath('//packet/chat')
                  if chat.text and chat.text.strip()]
    translated_chats = translate_multiple(
        (chat.text for chat in chats),
        language
    )
    for chat, translated_chat in zip(chats, translated_chats):
        chat.text = translated_chat
    return tostring(document, encoding='utf-8')


TRANSLATE_API_URL = 'https://translate.google.co.jp/'


def translate(text, language):
    """Translate text using Google Translate.
    Referred `Google Translator for Firefox`__ extension.

    __ http://translatorforfirefox.blogspot.com/

    """
    logger = logging.getLogger(__name__ + '.translate')
    response = post(
        TRANSLATE_API_URL,
        data={
            'text': text,
            'hl': language,
            'sl': 'ja',
            'js': 'n',
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'tl': language
        }
    )
    logger.debug('response status code: %d', response.status_code)
    logger.debug('response headers: %r', response.headers)
    html = re.sub(r'<script>.*?</script>', '\n', response.text)
    logger.debug('response body (HTML): %s', html)
    document = document_fromstring(response.content)
    result = document.xpath('descendant-or-self::*[@id="result_box"]')
    return result[0].xpath('string()')


BUFFER_LIMIT = 20000


def translate_multiple(text_list, language):
    """Translate many texts at a time."""
    text_list = list(text_list)
    boundary = ' {0} '.format(int(time.time() * random.randrange(1000, 9999)))
    total = len(text_list)
    result_list = []
    while len(result_list) < total:
        j = len(result_list)
        input_list = []
        buffer_limit = BUFFER_LIMIT
        while buffer_limit > 0:
            while j < total and sum(map(len, input_list)) < buffer_limit:
                input_list.append(text_list[j])
                input_list.append(boundary)
                j += 1
            translated = translate(''.join(input_list), language)
            split = re.split(r'\s*' + boundary.strip() + '\s*', translated)[:-1]
            if split:
                break
            buffer_limit //= 2
        result_list += split
    return result_list


def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port',
                      default=80,
                      help='port number to listen [%default]')
    parser.add_option('-H', '--host',
                      default='127.0.0.1',
                      help='host to listen [%default]')
    parser.add_option('-l', '-L', '--locale', '--lang', '--language',
                      dest='language',
                      metavar='LANG',
                      default=(locale.getlocale()[0] or 'en')[:2],
                      help='target language to translate to [%default]')
    parser.add_option('-d', '--debug',
                      dest='logging_level',
                      action='store_const',
                      const=logging.DEBUG,
                      default=logging.INFO,
                      help='print debug logs')
    options, args = parser.parse_args()
    if args:
        parser.error('take no arguments; use options instead')
    logging.basicConfig(level=options.logging_level, stream=sys.stderr)
    app = App(options.language)
    serve(app, host=options.host, port=options.port)


if __name__ == '__main__':
    main()
