# -*- coding: utf-8 -*-
"""Functions for manipulating external links or querying third-party sites."""
#
# (C) Pywikibot team, 2013-2019
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, division, unicode_literals

import json
from time import sleep
from xml.etree import ElementTree

from requests.exceptions import ConnectionError as RequestsConnectionError

from pywikibot.comms import http
from pywikibot import config2
from pywikibot.tools import issue_deprecation_warning, PY2

if not PY2:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

issue_deprecation_warning(
    'weblib', 'memento_client package', since='20150811',
    warning_class=FutureWarning)


def getInternetArchiveURL(url, timestamp=None):
    """Return archived URL by Internet Archive.

    See [[:mw:Archived Pages]] and https://archive.org/help/wayback_api.php
    for more details.

    @param url: url to search an archived version for
    @param timestamp: requested archive date. The version closest to that
        moment is returned. Format: YYYYMMDDhhmmss or part thereof.

    """
    uri = 'https://archive.org/wayback/available?'

    query = {'url': url}

    if timestamp is not None:
        query['timestamp'] = timestamp

    uri = uri + urlencode(query)

    retry_count = 0
    while retry_count <= config2.max_retries:
        try:
            jsontext = http.fetch(uri).text
            break
        except RequestsConnectionError as e:
            error = e
            retry_count += 1
            sleep(config2.retry_wait)
    else:
        raise error

    if 'closest' in jsontext:
        data = json.loads(jsontext)
        return data['archived_snapshots']['closest']['url']
    else:
        return None


def getWebCitationURL(url, timestamp=None):
    """Return archived URL by Web Citation.

    See http://www.webcitation.org/doc/WebCiteBestPracticesGuide.pdf
    for more details

    @param url: url to search an archived version for
    @param timestamp: requested archive date. The version closest to that
        moment is returned. Format: YYYYMMDDhhmmss or part thereof.

    """
    uri = 'http://www.webcitation.org/query?'

    query = {'returnxml': 'true',
             'url': url}

    if timestamp is not None:
        query['date'] = timestamp

    uri = uri + urlencode(query)
    xmltext = http.fetch(uri).text
    if 'success' in xmltext:
        data = ElementTree.fromstring(xmltext)
        return data.find('.//webcite_url').text
    else:
        return None
