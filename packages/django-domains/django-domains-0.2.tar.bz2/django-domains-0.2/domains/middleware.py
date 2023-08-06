# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from domains.utils import set_thread_variable
from django.conf import settings
from django.contrib.sites.models import Site


HOST_CACHE = {}


class RequestMiddleware(object):
    """
    Stores the request object in the local thread
    """
    def process_request(self, request):
        set_thread_variable('request', request)


class DynamicSiteMiddleware(object):
    """
    Define current Django Site for requested hostname
    """

    def process_request(self, request):
        host = request.get_host()
        shost = host.rsplit(':', 1)[0]  # just host, no port

        try:
            settings.SITE_ID.set(HOST_CACHE[host])
            return
        except KeyError:
            pass

        try:
            site = Site.objects.get(domain=host)
            HOST_CACHE[host] = site.pk
            settings.SITE_ID.set(site.pk)
            return
        except Site.DoesNotExist:
            pass

        if shost != host:  # get by hostname without port
            try:
                site = Site.objects.get(domain=shost)
                HOST_CACHE[host] = site.pk
                settings.SITE_ID.set(site.pk)
                return
            except Site.DoesNotExist:
                pass

        try:  # get by settings.SITE_ID
            site = Site.objects.get(pk=settings.SITE_ID)
            HOST_CACHE[host] = site.pk
            return
        except Site.DoesNotExist:
            pass

        try:  # misconfigured settings?
            site = Site.objects.all()[0]
            HOST_CACHE[host] = site.pk
            settings.SITE_ID.set(site.pk)
            return
        except IndexError:  # no sites in db
            pass
