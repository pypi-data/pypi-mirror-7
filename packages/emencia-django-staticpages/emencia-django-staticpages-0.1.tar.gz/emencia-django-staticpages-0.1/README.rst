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

In the settings : ::

    STATICPAGES = [
        ...
        (r'foo/$', "foo.html", 'mypage-foo'),
        ...
    ]

Then in your ``urls.py`` : ::

    url(r'^staticpages/', include('staticpages.urls')),

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
