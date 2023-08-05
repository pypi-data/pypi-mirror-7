import logging
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware, get_token, _sanitize_token, _get_new_csrf_key, REASON_NO_REFERER, REASON_NO_CSRF_COOKIE, REASON_BAD_TOKEN
from django.utils.crypto import constant_time_compare

logger = logging.getLogger('django.request')

class CsrfViewMiddleware(DjangoCsrfViewMiddleware):
    """CSRF view middleware that will ensure csrf token is always sent in cookie

    Strict Referer checking of https requests is removed"""

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, 'csrf_processing_done', False):
            return None

        try:
            csrf_token = _sanitize_token(
                request.COOKIES[settings.CSRF_COOKIE_NAME])
            # Use same token next time
            request.META['CSRF_COOKIE'] = csrf_token
        except KeyError:
            csrf_token = None
            # Generate token and store it in the request, so it's
            # available to the view.
            request.META["CSRF_COOKIE"] = _get_new_csrf_key()

        # Wait until request.META["CSRF_COOKIE"] has been manipulated before
        # bailing out, so that get_token still works
        if getattr(callback, 'csrf_exempt', False):
            return None

        # Assume that anything not defined as 'safe' by RFC2616 needs protection
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                # Mechanism to turn off CSRF checks for test suite.
                # It comes after the creation of CSRF cookies, so that
                # everything else continues to work exactly the same
                # (e.g. cookies are sent, etc.), but before any
                # branches that call reject().
                return self._accept(request)

            if csrf_token is None:
                # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
                # and in this way we can avoid all CSRF attacks, including login
                # CSRF.
                logger.warning('Forbidden (%s): %s',
                               REASON_NO_CSRF_COOKIE, request.path,
                    extra={
                        'status_code': 403,
                        'request': request,
                    }
                )
                return self._reject(request, REASON_NO_CSRF_COOKIE)

            # Check non-cookie token for match.
            request_csrf_token = ""
            if request.method == "POST":
                request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')

            if request_csrf_token == "":
                # Fall back to X-CSRFToken, to make things easier for AJAX,
                # and possible for PUT/DELETE.
                request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

            if not constant_time_compare(request_csrf_token, csrf_token):
                logger.warning('Forbidden (%s): %s',
                               REASON_BAD_TOKEN, request.path,
                    extra={
                        'status_code': 403,
                        'request': request,
                    }
                )
                return self._reject(request, REASON_BAD_TOKEN)

        resp = self._accept(request)

        request.META["CSRF_COOKIE_USED"] = True
        return resp
