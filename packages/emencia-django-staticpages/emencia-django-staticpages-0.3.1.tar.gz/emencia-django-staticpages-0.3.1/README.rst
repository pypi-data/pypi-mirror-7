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

All static page entries must defines three arguments :

* The regex pattern to match for the URL;
* The template path to use;
* The url name, that must be unique;

The raw way
-----------

In the settings : ::

    STATICPAGES = [
        ...
        (r'foo/$', "foo/index.html", 'foo-index'),
        (r'foo/part1/$', "foo/part1.html", 'foo-part1'),
        (r'foo/part2/$', "foo/part2.html", 'foo-part2'),
        ...
    ]

Then in your ``urls.py`` : ::

    url(r'^staticpages/', include('staticpages.urls.include')),

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

This method enables you to mount different static pages maps for your needs, opposite to the raw way you can use any setting name to store your page map. This is useful if you need to multiple separated page maps.

In the settings : ::

    FOO_STATICPAGES = (
        (r'foo/$', "foo/index.html", 'foo-index'),
        (r'foo/part1/$', "foo/part1.html", 'foo-part1'),
        (r'foo/part2/$', "foo/part2.html", 'foo-part2'),
    )

    BAR_STATICPAGES = (
        (r'bar/$', "bar/index.html", 'bar-index'),
        (r'bar/part1/$', "bar/part1.html", 'bar-part1'),
        (r'bar/part2/$', "bar/part2.html", 'bar-part2'),
    )

Then in your ``urls.py`` : ::

    from django.conf import settings
    from staticpages.urls import loaders

    urlpatterns = patterns('', *loaders.mount_staticpages(*settings.FOO_STATICPAGES)) + urlpatterns
    if settings.DEBUG:
        urlpatterns = patterns('', *loaders.mount_staticpages(*settings.BAR_STATICPAGES)) + urlpatterns

Note the usage of ``settings.DEBUG``, this is an example of the usage you can do of multiple separated page maps, the *bar* pages will not be published in production environnment but the *foo* pages will be.
    
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

Static page view
----------------

Also note that each page will use the view ``staticpages.views import StaticPageView``. This is just a inherit from ``django.views.generic.TemplateView`` that will contains a variable ``page_map``. This variable contains the used pages map. You can use it in your templates like so : ::

    <ul>{% for url_pattern,template_name,url_name in page_map %}
        <li><a href="{% url url_name %}">{{ template_name }}</a></li>
    {% endfor %}</ul>

This will list all available static pages in the pages map, useful to have an automatic browsable index of them.
