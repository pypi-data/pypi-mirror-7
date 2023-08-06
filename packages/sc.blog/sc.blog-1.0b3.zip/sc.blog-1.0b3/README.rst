=======
sc.blog
=======

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

This package includes a content type, views and viewlets to represent a blog
inside a Plone site.

Any content type inside a blog (except Image, File and Folder) can be a post.

Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/simplesconsultoria/sc.blog.png?branch=master
    :target: http://travis-ci.org/simplesconsultoria/sc.blog

.. image:: https://coveralls.io/repos/simplesconsultoria/sc.blog/badge.png?branch=master
    :target: https://coveralls.io/r/simplesconsultoria/sc.blog

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

Don't Panic
-----------

Installation
^^^^^^^^^^^^

To enable this product in a buildout-based installation:

#. Edit your buildout.cfg and add ``sc.blog`` to the list of eggs to
   install::

    [buildout]
    ...
    eggs =
        sc.blog

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``sc.blog`` and click the 'Activate' button.

.. Note::
    You may have to empty your browser cache and save your resource registries
    in order to see the effects of the product installation.

Usage
^^^^^

Just install the package and start adding Blogs and Posts.

A blog may have an associated image that is shown in a viewlet located below
the breadcrumb.

TODO List
^^^^^^^^^

* Navigation portlet listing posts on chronological order (refs. `#4`_)
* Tag Cloud portlet listing tags in posts (refs. `#6`_)

Not entirely unlike
-------------------

`blog.star`_
    A suite of blogging modules for Plone. It is primarily designed for
    integrators. Most people who use Plone for blogging also uses Plone as a
    customized content management system, and they have specific requirements
    and their own skin, custom content types and other integrations. It turned
    out that other Plone blogging products make a lot of assumption about how
    you are to use it, what you want from a blog, and how your site is set up.


`ftw.blog`_
    ftw.blog provides a blog implementation for Plone featuring tags and
    categories. A user can add a new blog entry and tag it using tags and
    categories. Available categories are defined by the creator of the blog,
    whilst tags can be added freely by the author of a blog entry. Blog
    entries are listed in chronological order, in a tag cloud, by categories,
    and in a monthly archive. Entries can be searched by using the search
    function of the blog.

`Scrawl`_
    A dirt-simple blog product for Plone. It copies the News Item content type
    to create a Blog Entry (with a slightly tweaked view template) and adds an
    alternative view to Collections (blog_view). Note that blog_view shows
    either the description of each contained blog entry (if it exists) or the
    entire body. It's up to the user to limit those results in an intelligent
    way so that page loads doesn't take too long.

.. _`#4`: https://github.com/simplesconsultoria/sc.blog/issues/4
.. _`#6`: https://github.com/simplesconsultoria/sc.blog/issues/6
.. _`blog.star`: https://pypi.python.org/pypi/collective.blog.star
.. _`collective.nitf`: https://github.com/collective/collective.nitf
.. _`ftw.blog`: https://pypi.python.org/pypi/ftw.blog
.. _`opening a support ticket`: https://github.com/simplesconsultoria/sc.blog/issues
.. _`Scrawl`: https://pypi.python.org/pypi/Products.Scrawl
