djehuty
=======

post webhook manager written in Python

environment
-----------

- Python2.7 expected.

install
-------

You can use pip.

::

  $ pip install djehuty

create djehuty app on heroku
----------------------------

::

   $ pcreate -s djehuty_server YOUR_PROJECT_NAME
   $ cd YOUR_PROJECT_NAME
   $ git init
   $ heroku create

You can add existing services(slack only now)...::

  --- a/production.ini
  +++ b/production.ini
  @@ -8,6 +8,7 @@ pyramid.debug_routematch = false
   pyramid.default_locale_name = en
   pyramid.includes =
          djehuty
  +        djehutyslack

or implement your custom service in YOUR_PROJECT_NAME/YOUR_PROJECT_NAME/services.py.

implement custom service
------------------------

not yet.

implement and add custom command
------------------------

djehuty.command.Command is a almost cliff<http://cliff.readthedocs.org/en/latest/> command.After implementing your command, add command name and command class module path in setup.py entry_points.

todo
----

- Python 3 support
- unit test
