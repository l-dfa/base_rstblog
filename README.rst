
rstblog
===========

``rstblog`` is a simple blog driven by articles written using
the reStructuredText_ markup language.

It's developed using Django_, based on the Python_ language.

The basic idea is to adopt a *hybrid* publication model,
halfway between a static site (pure html) and a dynamic one (all inside a DB,
as Wordpress_).

In practice, the author writes his article locally, at his/her PC,
in a text file, using a markup language.

After that:

* he puts a series of lines at the top of the article; they serve to
  categorize it, indicating the language used, the title, and other attributes ...
* and a line of text, of fixed format, which separates the attributes from the 
  article content.

Finally he calls an address (URL) of the site that allows him to upload the article.
If the user is not logged in to the site, this address asks for user and password.

When the article is uploaded to the site, ``rstblog`` uses its attributes
to classify it in the database. The content of the article is not loaded
in the DB; when necessary, it is resumed from the file uploaded on the site.

If the author wants to modify the content of the article (or its attributes),
he edits the file on his PC, then upload it again.

As markup language you can use:

* html_;
* Markdown_;
* reStructuredText_.

What are the reasons that led us to this design choice? The following:

* we can always count on a local backup of all the contents of the site;
* we can work without an Internet connection, and connect only when
  we want to upload;
* the program is extremely light, it runs smoothly on servers with
  limited CPU capacity as with little RAM and HDU space (as long as accesses
  are contained, and we haven't this problem :-);
* we do not renounce the flexibility and speed of research that a DB allows me;
* if we have a few articles [1]_ the DB can be implemented with the support library
  of Python (``sqlite3``), without using big programs (in the sense
  that they commit a lot of resources) like MySQL_, PostgreSQL_, ...

The project consists of a demo site and the Django application ``rstblog``.

The features that the project currently implements are:

* the index of articles, indicating the number of consultations
  of each article and the main attributes;
* display of an article (or a page of the site);
* upload of an article (or a page of the site);
* complete reconstruction of the DB starting from the files of the articles uploaded to the site;
* administration of the DB contents (who knows Django knows that I'm cheating:
  in the Django development environment this functionality is embedded);
* generation of the site's ``sitemap.xml``;
* articles may have translations, they can be present in more than one language;
* indication of site statistics; in the sense of how many articles are
  loaded, how many languages ​​are used, how many articles are present in each
  classification topic and language.
  
What are the contraindications to the use of this environment? You must have a
good knowledge of Python/Django to:

* customize the project to your needs;
* install it in a production server.
  
If all this does not scare you, and you are the adventurous guy:

* this is the `project repository <https://github.com/l-dfa/base_rstblog.git>`_;
* and here are (sorry: still incomplete) `the manuals <https://rstblog.readthedocs.io/en/latest/index.html>`_.

Here there is `the author’s website <https://luciano.defalcoalfano.it>`_.
Its contents are mainly written in italian language
and, could you guess?, it's implemented using this project.

This work is distributed under a 
`CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>`_
license.




------------------------------

.. _Python: http://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _MySQL: https://dev.mysql.com/downloads/
.. _PostgreSQL: https://www.postgresql.org/community/

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: https://daringfireball.net/projects/markdown/syntax
.. _html: https://www.w3.org/TR/2017/REC-html52-20171214/
.. _Wordpress: https://wordpress.org/

.. [1] Not so few: with hundreds articles, everything reacts well.
  
