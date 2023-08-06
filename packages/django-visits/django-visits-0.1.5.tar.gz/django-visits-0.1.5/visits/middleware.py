# -*- coding: utf-8 -*-
from visits import settings
from visits.models import Visit
from django.core.urlresolvers import resolve


class CounterMiddleware(object):
    """ Middleware for count uri visits. """

    def process_request(self, request):
        app_name = ''
        try:
            app_name = resolve(request.path)
        except BaseException:
            pass

        if settings.URI_WITH_GET_PARAMS:
            Visit.objects.add_uri_visit(request, request.get_full_path(), app_name)
        else:
            Visit.objects.add_uri_visit(request, request.path_info, app_name)


class BotVisitorMiddleware(object):
    """ Middleware for count uri visits for bots. """

    def process_request(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT", None)
        if user_agent in settings.BOTS_USER_AGENTS:
            request.META.setdefault("IS_BOT", True)
        else:
            request.META.setdefault("IS_BOT", False)
