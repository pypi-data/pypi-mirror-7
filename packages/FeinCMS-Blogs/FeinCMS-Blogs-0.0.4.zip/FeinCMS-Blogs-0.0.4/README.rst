=============
FeinCMS blogs
=============

A simple app for having multiple FeinCMS powered blogs on a django site.


Installation
============
Install from pypi using your favorite method:::

    pip install feincms-blogs


Usage
=====

Add ``blogs`` to your ``INSTALLED_APPS``.

Somewhere in your project (ideally a ``models.py`` file):::

    from blogs.models import Post
    
    Post.register_extensions(
        # These are an example - you can use whichever extensions you like
        'feincms.module.extensions.ct_tracker',
        'feincms.module.extensions.changedate',
        'feincms.module.extensions.datepublisher',
        'feincms.module.extensions.seo',
    )

    Post.register_templates(
        {'title': 'Post',
         'path': 'blogs/post.html',
         'regions': (
             ('main', 'Main content area'),
         )},
    )
    
    Post.create_content_type(RichTextContent)

And then in in your ``urls.py``:::

    urlpatterns = urlpatterns + patterns(
        url(r'^blogs/', include('blogs.urls', namespace="blogs")),
    )

This should look familiar if you've used FeinCMS.

There are some content types provided for use with (for example) your FeinCMS
Pages:::

    from blogs.content import (
        RecentPostsListContent,
        BlogArchiveContent,
    )

    from feincms.module.page.models import Page

    Page.create_content_type(RecentPostsListContent)
    Page.create_content_type(BlogArchiveContent)
