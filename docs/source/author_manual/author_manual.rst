
.. _author manual:

author manual
=================

.. contents:: author manual table of contents
   :depth: 3
   
Let's speak how organize an article that we'll publish using ``rstblog``.

It is written in a file with two parts. The first part is about fields
categorizing our article. The second part has content of the article.

The two parts are separated by a line containing the string::

  .. hic sunt leones
  
Yes: two dots, space, and the phrase *hic sunt leones*. No more, no less, in a
single line [#]_.

So, reiterating the concept, we have this schema: 

  | *fields area* (generally: one field every line)
  | optional empty line
  | ``.. hic sunt leones``
  | optional empty line
  | *article contents*

Hereafter, as example, we report first lines of an
_`article about Marco Tullius Cicero`, whose content is extracted from 
wikipedia. It's written using reST:

.. code-block:: none

  :markup: restructuredtext
  :language: en
  :title: Speaking about Cicero
  :created: 2018-08-05 10:00:00
  :modified: 2018-08-05 10:00:00
  :slug: speaking-about-cicero
  :summary:  The Marcus Cicero's profile: informations and life.
  :author:   Wikipedia
  :category: latin literature history
  
  .. hic sunt leones
  
  Speaking about Cicero
  ======================
  
  *Marcus Tullius Cicero* was a Roman statesman, orator, lawyer
  and philosopher, who served as consul in the year 63 BC.
  He came from a wealthy municipal family of the Roman equestrian
  order, and is considered one of Rome's greatest orators
  and prose stylists.

  ...

A last general information about article file. How to name it? Our advice
is: create a rule and follow it. So you'll have a clearer
working area.

As example, you can use a progressive number and a very short title note.

But whatever rule you'll adopt, it will be right: ``rstblog`` is filename
agnostic. Just a caution: it would be better if file extension is related
to the format used; i.e.: ``.md`` for *markdown* text, ``.rst`` for *reST* text
and ``.html`` for *html* text.

Now we'll speak in more detail about fields and content areas.

Fields
-----------

As we saw, fields categorize our article. So they are vital.

``rstblog`` uses fields shown in previous example
`article about Marco Tullius Cicero`_. There is one more, but we'll 
talk about it in a while.

By now, we exhort you to use all the fields shown in the example
and to pay attention to typos. At this early stage of development 
(v0.2 as we write) there aren't a lot of controls about syntax errors.

A single field has structure:

  ``:``\ **fieldname**\ ``:`` *fieldvalue*
  
``rstblog`` decides **fieldname**\ (s). So you must use the right fieldame
without typos. Instead what to put in *fieldvalue* is up to you.

Let's see the single fields meaning.

markup
^^^^^^^

This specify what markup language you use *to write article content*. Note the
phrase *article content*. In fact field area is ever written
using reST syntax.

Acceptable values for this field are: ``markdown``, ``restructuredtext`` [#]_,
``html``.

Example::

  :markup: restructuredtext
  
language
^^^^^^^^

This is about what language you use to write the article content.

Acceptable values are defined from your site configuration. And it's
the site master responsability to configure it. Probably, at least
english (written as ``en``) would be available. Languages are invoked
using their abbreviations; i.e. ``it`` for italian, ``fr`` for french, 
``es`` for spanish, and so on.

Example::

  :language: it
  
title
^^^^^^

This is the article title. It is shown in the blog index to identify
your article and as a link to read it.

Acceptable values: whatever you want, provided that there are no other
articles with the same title in the blog. Article title must be unique
in the site.

Example:

  :title: Speaking about Cicero
  
created and modified 
^^^^^^^^^^^^^^^^^^^^

These are two fields showing:

* the first the article  creation date and time;
* and the second the article last modified date and time.

Acceptable values. Whatever, in the format: 
**YYYY**\ ``-``\ **MM**\ ``-``\ **DD** **HH**\ ``:``\ **MM**\ ``:``\ **SS**

Example:

  :created: 2018-08-05 10:00:00
  :modified: 2018-08-05 10:00:00
  
slug
^^^^^^

Slug is the last piece of information used in the URL to reach your article.
usually it reflects the article title to help the reader (and the web
crawler programs) to remember the article title.

Acceptable values. As titles, even slugs must be unique in the blog. 
Futhermore, they must be composed of a subset of ansi characters. To stay
smooth, it's usual to use only lowercase regular letters, with puntuation marks
and spaces substitued by dashes.

Example. If your article would be reached by this url:
``https://my.blog.org/blog/speaking-about-cicero``, you'll use::

  :slug: speaking-about-cicero
  
summary
^^^^^^^^

This field value summarizes your article content. It is shown in the 
blog index page after the title of article.

Accepted values. No restrictions here. And this field can accept even
multiple lines contents. If you want to use multiple lines, you need
to indent it from the second line on.

Example of multiple lines summary:

  :summary:  The Marcus Cicero's profile: informations and life. From
      wikipedia in english language.

author
^^^^^^^

Put here the name of author of the article (your name, I suppose :-).

Accepted values. Author name must be present in blog database. It is 
responsability of site manager to insert the names of accepted authors.

Example:

  :author:   Lawrence of Arabia
  
category
^^^^^^^^

this is the master of categorizations. It catalogs our article assigning
it to a main type.

Accepted values. Again, it depends on the configuration of your blog.
It is responsability of site manager to insert the accepted categories
in the blog database. And only  values present in this database are
accepted by ``rstblog``.

Example::

  :category: latin literature history

translation_of
^^^^^^^^^^^^^^^

Surprise: a field name not quoted in the `article about Marco Tullius Cicero`_!
What is this? You can send to ``rstblog`` even articles that are translations
of article already known by ``rstblog``. If is this the case, in this field
you write the title of the *original* (translated) article.

Accepted values. A title of an article present in the blog database.

Example. If you write a translation of `article about Marco Tullius Cicero`_,
it could be as follow:

.. code-block:: none

  :markup: restructuredtext
  :language: it
  :title: Parlando di Cicerone
  :created: 2018-08-05 10:00:00
  :modified: 2018-08-05 10:00:00
  :slug: parlando-di-cicerone
  :summary:  Il profilo di Marco Tullio Cicerone: notizie e vita.
  :author:   Wikipedia
  :category: latin literature history
  :translation_of: Speaking about Cicero
  
  .. hic sunt leones
  
  Parlando di Cicerone
  ====================
  
  *Marco Tullio Cicerone* è stato uno statista Romano, oratore, avvocato
  e filosofo, che ha servito come console nell'anno 63 AC.
  Veniva da una agiata famiglia cittadina dell'ordine Romano degli Equestri,
  ed è considerato uno dei più grandi oratori e scrittori di Roma.

  ...
  
As you can see, in the fields area of this translation, we changed:

* the language indicator, to reflect the new language used in the translation;
* the title (remember: two equal titles aren't possible in the same blog);
* the slug (like above: no equal slugs in the blog, and we would match
  as near possible the title);
* the summary (maybe it would be read from Italians ...).

And we added:

* the **translation_of** field, with a value of ``Speaking about Cicero``, the 
  title of translated article.
  

Content
-----------

What to say about content?

Here the author develops his true work: to write the articles contents.

You are free to choose the format type you like throught *markdown*,
*reST* and *html*.

Let us to give you just some advices about other files you could refer
from your article.

First of all: the external hyperlinks. These are html pages available
thanks to other sites. And all three quoted formats allow to refer them.
As an example, this is an external hyperlink to wikipedia main page 
using reST::

  `wikipedia <https://en.wikipedia.org/wiki/Main_Page>`_

It shows word ``wikipedia`` and it jumps to its main page if you are clicking
on the word.

Then, what about hyperlink to other article in the site? In this case, 
use the (relative) article URL. Remember: it uses ``blog/`` as prefix, 
and slug as article identifier. So to hyperlink to your article 
*Speaking about Cicero* you can use (for example)::

  ...
  you can read our wonderful `article about Cicero </blog/speaking-about-cicero>`_
  ...
  
Note that it isn't necessary to report the site domain (``my.blog.org``), and
we use the article slug.

And, last but not least, how hyperlink to other files (not articles) present
in our site? Here we need some technical clarifications to keep in touch.

In our site, files that aren't articles can live on these directories:

* ``pages`` that hosts the site pages that aren't articles;
* ``media`` that hosts other type of files, such as images, 
  audio, video, pdf, and so on.
  
Usually ``media`` has one subdirectory for every kind of hosted file. I.e.:

* ``media/images`` to keep images;
* ``media/pdfs`` to store pdf files, and so on.

As you can argue, if you would hyperlink to ``mylife.pdf`` file, you can 
use::

  ...
  `here </media/pdfs/mylife.pdf>`_ you can know something more about my life.
  ...

By now, these files must be uploaded to your site using some other kind of
software; maybe ftp, or remote copy. This means that you must be
a true site administrator to handle this files. If this is a problem
for you: stay tuned ... In the future it's
possible ``rstblog`` could upload even these files with the article.

A very last note. When you would publish your work, you need to call:

  ``https://my.blog.org/blog/load-article``
  
``rstblog`` will ask you for your username and password. When you'll
give them to it, it will ask for the article filename to load. Here you can
browse to the article file [#]_ and submit it, loading the request file.
  
That's all folk about author manual. 
Thank you to read it. We hope you enjoy it.




.. [#] A point to rember. If you wish, this signal could be changed
   by the *site manager*. And an anecdote. People say that this phrase was used in
   the maps of ancient Rome, to indicate unexplored territories of Africa.
   But there is no firm evidence that this is true. In this context we 
   adopt it to indicate that from here on we enter the unknown meanders
   of the creation of the article.
   
.. [#] Note the use of the full name of the sintax type.

..[#] Or directly type it, if you remember its full path and name.