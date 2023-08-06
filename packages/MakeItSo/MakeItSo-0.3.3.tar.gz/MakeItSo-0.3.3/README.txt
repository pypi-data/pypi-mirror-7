Make It So!
===========

/templates for the people/

So people generally do things the easiest way possible.  If you try to
get people to send you a file with, say, a "one-off" script, they will
probably hard code a bunch of stuff in it.  Then, you're not really
sure what needs to be changed and because you're human you might make
a mistake.  Worse, its a perl script and you're a python programmer.
You don't know what that script does!

And this is the time of the iceberg.  If it really is a one-off, who
cares?  But quickly one-offs become a deployment story, and not a very
efficient one.


Making a New Template
---------------------


Variable Conventions
--------------------

MakeItSo! provides a few variables for you.  You can include another
file or URL using {{include(URI)}}, where URI is the file path or the
URL (of course, internet is required to include remote resources). The
included resource is not included.

Files and URLS being interpolated also have the variable %(here)s,
which is the parent of their resource.  Therefor, using sensible path
conventions, a neighboring file may be (e.g.) included like

{{include(here + 'foo.txt')}}

The python template asserts several conventions:

- project: the project chosen
- author: author of a project
- email: author's email
- url: url of the project
- repo: the repository of the project; this will be used for the URL
        if it is given and the URL is not


Adding a License to a Template
------------------------------

[TODO]


Web Service
-----------

python has the ability to run files from stdin.  This means you can
run makeitso directly from the web::

 python <(curl http://k0s.org/mozilla/hg/MakeItSo/raw-file/tip/makeitso/makeitso.py) [URI]

This uses the bash shell.  If you have another shell you may have to
use another syntax, download the file, or install the package.


Similar Projects
----------------

* http://cookiecutter.readthedocs.org/ ,
  https://github.com/audreyr/cookiecutter

* https://github.com/lucuma/Voodoo
