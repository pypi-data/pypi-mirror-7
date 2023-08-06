Introduction
============

This is a simple Django app to publish some pages directly from templates. 

Yes, this is simply to use a ``django.views.generic.TemplateView`` but this app will help to manage many pages and with Django sitemaps support.

Install
=======

Add it to your installed apps in the settings : ::

    INSTALLED_APPS = (
        ...
        'staticpages',
        ...
    )

Usage
=====

The raw way
-----------

In the settings : ::

    STATICPAGES = [
        ...
        (r'foo/$', "foo.html", 'foo-mypage'),
        ...
    ]

Then in your ``urls.py`` : ::

    url(r'^staticpages/', include('staticpages.urls.include')),

And so your page ``mypage-foo`` will be published on ``/staticpages/foo/`` using the ``foo.html`` template.

If you want to publish them in your ``sitemap.xml`` with Django sitemaps, you will have to do something like this in your ``urls.py`` : ::

    from staticpages.sitemaps import StaticPageSitemapBase, StaticPageEntryTemplate

    class MypagesSitemap(StaticPageSitemapBase):
        page_entries = [
            StaticPageEntryTemplate(url_name='mypage-foo', template_name='foo.html'),
        ]

    # Enabled sitemaps
    sitemaps = {
        # For Prototypes
        'mypages': MypagesSitemap,
    }

    urlpatterns += patterns('django.contrib.sitemaps.views',
        url(r'^sitemap\.xml$', 'sitemap', {'sitemaps': sitemaps}),
    )

The semi-auto way
-----------------

This method enables you to mount different static pages maps for your needs, opposite to the raw way you can use any setting name to store your page map.

In the settings : ::

    FOO_STATICPAGES = (
        ...
        (r'foo/$', "foo.html", 'foo-mypage'),
        ...
    )

    BAR_STATICPAGES = (
        ...
        (r'bar/$', "bar.html", 'bar-mypage'),
        ...
    )

Then in your ``urls.py`` : ::

    from django.conf import settings
    from staticpages.urls import loaders

    urlpatterns = patterns('', *loaders.mount_staticpages(*settings.FOO_STATICPAGES)) + urlpatterns
    urlpatterns = patterns('', *loaders.mount_staticpages(*settings.BAR_STATICPAGES)) + urlpatterns
    
So your page ``foo-mypage`` will be published on ``/foo/`` and ``bar-mypage`` will be published on ``/bar/``.

Also for the ``sitemap.xml`` with Django sitemaps, you will have to do something like this in your ``urls.py`` : ::

    from django.conf import settings
    from staticpages.sitemaps import StaticPageSitemapAuto

    class FooSitemap(StaticPageSitemapAuto):
        pages_map = settings.FOO_STATICPAGES

    class BarSitemap(StaticPageSitemapAuto):
        pages_map = settings.BAR_STATICPAGES


    # Enabled sitemaps
    sitemaps = {
        'foo': FooSitemap,
        'bar': BarSitemap,
    }

    urlpatterns += patterns('django.contrib.sitemaps.views',
        url(r'^sitemap\.xml$', 'sitemap', {'sitemaps': sitemaps}),
    ) + urlpatterns
