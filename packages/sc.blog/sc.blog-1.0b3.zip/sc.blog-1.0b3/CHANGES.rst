Changelog
---------

There's a frood who really knows where his towel is.

1.0b3 (2014-06-26)
^^^^^^^^^^^^^^^^^^

- The ``IExcludeFromNavigation`` behavior is now enabled by default.
  [hvelarde]


1.0b2 (2013-12-16)
^^^^^^^^^^^^^^^^^^

- Fix issue accessing blogs with VHM urls (closes `#9`_). [jpgimenez]

- The method that returns the content types that are considered blog posts
  was fixed and renamed from ``query_portal_types`` to
  ``get_blog_friendly_types``.
  [hvelarde]


1.0b1 (2013-11-11)
^^^^^^^^^^^^^^^^^^

- Add support for object relations. [hvelarde]

- RobotFramework tests (closes `#7`_). [jpgimenez]

- Implements recursion into views to display posts than there are inside
  subfolders of the blog (closes `#5`_). [jpgimenez]

- Fix blog_summary_view (closes `#3`_). [jpgimenez]


1.0a5 (2013-10-30)
^^^^^^^^^^^^^^^^^^

- Remove dependency on collective.nitf; now any content type inside a blog
  (except Image, File and Folder) can be a post. [jpgimenez]


1.0a4 (2013-05-02)
^^^^^^^^^^^^^^^^^^

- Register static resource directory manually as Grok no longer does it.
  Package is now Plone 4.3 compatible. [hvelarde]


1.0a3 (2013-04-10)
^^^^^^^^^^^^^^^^^^

- Refactor template of blog header: now it will display the blog image, if
  present, or the blog title, if not. [hvelarde]

- Image field is no longer required by default. [hvelarde]

- In order to fix ordering in plone.abovecontent viewlet manager, we had to
  register the plone.path_bar viewlet before everything and then register the
  sc.blog.blogheader viewlet after everything. [hvelarde]


1.0a2 (2013-04-04)
^^^^^^^^^^^^^^^^^^

- Fix batch size and ordering of posts on blogs. Now up to 10 posts are shown
  per page and they are sorted by effective date in descending order.
  [hvelarde]

- Disallow comments on blogs by default as users comment on posts. [hvelarde]


1.0a1 (2013-03-15)
^^^^^^^^^^^^^^^^^^

- Initial release.

.. _`#3`: https://github.com/simplesconsultoria/sc.blog/issues/3
.. _`#5`: https://github.com/simplesconsultoria/sc.blog/issues/5
.. _`#7`: https://github.com/simplesconsultoria/sc.blog/issues/7
.. _`#9`: https://github.com/simplesconsultoria/sc.blog/issues/9
