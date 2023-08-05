import logging
import re

try:
    from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
except ImportError:  # pragma: no cover
    from urllib import urlencode
    from urlparse import parse_qsl, urlparse, urlunparse

from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponseRedirect


logger = logging.getLogger(__name__)


def add_query_params(url, params):
    """
    Inject additional query parameters into an existing URL. If
    parameters already exist with the same name, they will be
    overwritten. Return the modified URL as a string.
    """
    # Ignore additional parameters with empty values
    params = dict([(k, v) for k, v in params.items() if v])
    parts = list(urlparse(url))
    query = dict(parse_qsl(parts[4]))
    query.update(params)
    parts[4] = urlencode(query)
    return urlunparse(parts)


def is_scheme_https(url):
    """
    Test the scheme of the parameter URL to see if it is HTTPS. If
    it is HTTPS return ``True``, otherwise return ``False``.
    """
    return 'https' == urlparse(url).scheme


def clean_service_url(url):
    """
    Return only the scheme, hostname (with optional port) and path
    components of the parameter URL.
    """
    parts = urlparse(url)
    return urlunparse((parts.scheme, parts.netloc, parts.path, '', '', ''))


def is_valid_service_url(url):
    """
    Check the provided URL against the configured list of valid service
    URLs. If the service URL matches at least one valid service, return
    ``True``, otherwise return ``False``. If no valid service URLs are
    configured, return ``True``.
    """
    valid_services = getattr(settings, 'MAMA_CAS_VALID_SERVICES', ())
    if not valid_services:
        return True
    for service in [re.compile(s) for s in valid_services]:
        if service.match(url):
            return True
    return False


def redirect(to, *args, **kwargs):
    """
    Similar to the Django ``redirect`` shortcut but with altered
    functionality. If an optional ``params`` argument is provided, the
    dictionary items will be injected as query parameters on the
    redirection URL.
    """
    params = kwargs.pop('params', {})

    try:
        to = urlresolvers.reverse(to, args=args, kwargs=kwargs)
    except urlresolvers.NoReverseMatch:
        if '/' not in to and '.' not in to:
            to = urlresolvers.reverse('cas_login')

    if params:
        to = add_query_params(to, params)

    logger.debug("Redirecting to %s" % to)
    return HttpResponseRedirect(to)
