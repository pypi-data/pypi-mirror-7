# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys
from cms.apphook_pool import apphook_pool
from cms.utils.compat.type_checks import string_types
from cms.utils.i18n import force_language, get_language_list
from cms.models.pagemodel import Page

from django.conf import settings
from django.conf.urls import patterns
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import RegexURLResolver, Resolver404, reverse, \
    RegexURLPattern
from django.utils.importlib import import_module
from django.utils.translation import get_language

APP_RESOLVERS = []


def clear_app_resolvers():
    global APP_RESOLVERS
    APP_RESOLVERS = []


def applications_page_check(request, current_page=None, path=None):
    """Tries to find if given path was resolved over application.
    Applications have higher priority than other cms pages.
    """
    if current_page:
        return current_page
    if path is None:
        # We should get in this branch only if an apphook is active on /
        # This removes the non-CMS part of the URL.
        path = request.path.replace(reverse('pages-root'), '', 1)
        # check if application resolver can resolve this
    for lang in get_language_list():
        if path.startswith(lang + "/"):
            path = path[len(lang + "/"):]
    for resolver in APP_RESOLVERS:
        try:
            page_id = resolver.resolve_page_id(path)
            # yes, it is application page
            page = Page.objects.public().get(id=page_id)
            # If current page was matched, then we have some override for content
            # from cms, but keep current page. Otherwise return page to which was application assigned.
            return page
        except Resolver404:
            # Raised if the page is not managed by an apphook
            pass
    return None


class AppRegexURLResolver(RegexURLResolver):
    def __init__(self, *args, **kwargs):
        self.page_id = None
        self.url_patterns_dict = {}
        super(AppRegexURLResolver, self).__init__(*args, **kwargs)

    @property
    def url_patterns(self):
        language = get_language()
        if language in self.url_patterns_dict:
            return self.url_patterns_dict[language]
        else:
            return []

    def resolve_page_id(self, path):
        """Resolves requested path similar way how resolve does, but instead
        of return callback,.. returns page_id to which was application
        assigned.
        """
        tried = []
        match = self.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in self.url_patterns:
                if isinstance(pattern, AppRegexURLResolver):
                    try:
                        return pattern.resolve_page_id(new_path)
                    except Resolver404:
                        pass
                else:
                    try:
                        sub_match = pattern.resolve(new_path)
                    except Resolver404:
                        exc = sys.exc_info()[0]
                        if 'tried' in exc.args[0]:
                            tried.extend([[pattern] + t for t in exc.args[0]['tried']])
                        elif 'path' in exc.args[0]:
                            tried.extend([[pattern] + t for t in exc.args[0]['path']])
                    else:
                        if sub_match:
                            return pattern.page_id
                        tried.append(pattern.regex.pattern)
            raise Resolver404({'tried': tried, 'path': new_path})


def recurse_patterns(path, pattern_list, page_id, default_args=None):
    """
    Recurse over a list of to-be-hooked patterns for a given path prefix
    """
    newpatterns = []
    for pattern in pattern_list:
        app_pat = pattern.regex.pattern
        # make sure we don't get patterns that start with more than one '^'!
        app_pat = app_pat.lstrip('^')
        path = path.lstrip('^')
        regex = r'^%s%s' % (path, app_pat)
        if isinstance(pattern, RegexURLResolver):
            # this is an 'include', recurse!
            resolver = RegexURLResolver(regex, 'cms_appresolver',
                                        pattern.default_kwargs, pattern.app_name, pattern.namespace)
            resolver.page_id = page_id
            # include default_args
            args = pattern.default_kwargs
            if default_args:
                args.update(default_args)
            # see lines 243 and 236 of urlresolvers.py to understand the next line
            resolver._urlconf_module = recurse_patterns(regex, pattern.url_patterns, page_id, args)
        else:
            # Re-do the RegexURLPattern with the new regular expression
            args = pattern.default_args
            if default_args:
                args.update(default_args)
            resolver = RegexURLPattern(regex, pattern.callback,
                                       args, pattern.name)
            resolver.page_id = page_id
        newpatterns.append(resolver)
    return newpatterns


def _flatten_patterns(patterns):
    flat = []
    for pattern in patterns:
        if isinstance(pattern, RegexURLResolver):
            flat += _flatten_patterns(pattern.url_patterns)
        else:
            flat.append(pattern)
    return flat


def get_app_urls(urls):
    for urlconf in urls:
        if isinstance(urlconf, string_types):
            mod = import_module(urlconf)
            if not hasattr(mod, 'urlpatterns'):
                raise ImproperlyConfigured(
                    "URLConf `%s` has no urlpatterns attribute" % urlconf)
            yield getattr(mod, 'urlpatterns')
        else:
            yield urlconf


def get_patterns_for_title(path, title):
    """
    Resolve the urlconf module for a path+title combination
    Returns a list of url objects.
    """
    app = apphook_pool.get_apphook(title.page.application_urls)
    url_patterns = []
    for pattern_list in get_app_urls(app.urls):
        if path and not path.endswith('/'):
            path += '/'
        page_id = title.page.id
        url_patterns += recurse_patterns(path, pattern_list, page_id)
    url_patterns = _flatten_patterns(url_patterns)
    return url_patterns


def get_app_patterns():
    """
    Get a list of patterns for all hooked apps.

    How this works:

    By looking through all titles with an app hook (application_urls) we find all
    urlconf modules we have to hook into titles.

    If we use the ML URL Middleware, we namespace those patterns with the title
    language.

    All 'normal' patterns from the urlconf get re-written by prefixing them with
    the title path and then included into the cms url patterns.
    """
    from cms.models import Title

    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        current_site = None
    included = []

    # we don't have a request here so get_page_queryset() can't be used,
    # so use public() queryset.
    # This can be done because url patterns are used just in frontend

    title_qs = Title.objects.public().filter(page__site=current_site)

    hooked_applications = {}

    # Loop over all titles with an application hooked to them
    for title in title_qs.exclude(page__application_urls=None).exclude(page__application_urls='').select_related():
        path = title.path
        mix_id = "%s:%s:%s" % (path + "/", title.page.application_urls, title.language)
        if mix_id in included:
            # don't add the same thing twice
            continue
        if not settings.APPEND_SLASH:
            path += '/'
        if title.page_id not in hooked_applications:
            hooked_applications[title.page_id] = {}
        app = apphook_pool.get_apphook(title.page.application_urls)
        app_ns = app.app_name, title.page.application_namespace
        with force_language(title.language):
            hooked_applications[title.page_id][title.language] = (app_ns, get_patterns_for_title(path, title))
        included.append(mix_id)
        # Build the app patterns to be included in the cms urlconfs
    app_patterns = []
    for page_id in hooked_applications.keys():
        resolver = None
        for lang in hooked_applications[page_id].keys():
            (app_ns, inst_ns), current_patterns = hooked_applications[page_id][lang]
            if not resolver:
                resolver = AppRegexURLResolver(r'', 'app_resolver', app_name=app_ns, namespace=inst_ns)
                resolver.page_id = page_id
            extra_patterns = patterns('', *current_patterns)
            resolver.url_patterns_dict[lang] = extra_patterns
        app_patterns.append(resolver)
        APP_RESOLVERS.append(resolver)
    return app_patterns
