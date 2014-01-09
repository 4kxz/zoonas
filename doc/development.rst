
Setting up development
======================

Requirements
------------

-  git
-  postgresql
-  python (2.7)
-  python-pip
-  sass

postgresql
----------
Install from repo, anything >= 9.2 should do.

You need to create a database, any tutorial for your distro should work.

In Arch it can be done with:

::

    $ su postgres -c 'initdb -D ~/db-folder'
    $ su postgres -c 'postgres -D ~/db-folder/'

Set a user and password that with access to the database and you’re good to go.

git
---
Install git if necessary. Remember to configure it:

::

  $ git config --global user.name ‘User’
  $ git config --global user.email ‘user@example.com’
  $ git config --global color.ui true

Clone the repository:

::

  $ git clone git@bitbucket.org:c2x3/zoonas.com.git

Next, you should create a virtualenv and install the other Python dependencies. To do that you’re going to need pip.

pip
---
In Arch it’s in the ``python-pip`` package, most distros should have a package for it.

Virtualenv
----------
It’s a good idea to use a virtualenv to avoid package conflicts and such. They’re easy to manage using virtualenvwrapper:

::

  $ pip install virtualenvwrapper

Next, add at the end of your .bashrc (or whatever you use):

::

  export WORKON_HOME='$HOME/.virtualenvs'
  source `which virtualenvwrapper.sh`

Or, in Ubuntu:

::

  export WORKON_HOME='$HOME/.virtualenvs'
  source /usr/local/bin/virtualenvwrapper.sh

You should be able to use the virtualenv commands (if it doesn’t work straight away try a new terminal first).

Create a virtualenv, specifying the Python version, and without using local packages:

::

  $ mkvirtualenv -p /usr/bin/python2.7 --no-site-packages --distribute zoonas

Your prompt should change to indicate that you’re working on the virtualenv. To disable it just type:

::

  $ deactivate

To load it again:

::

  $ workon zoonas

SCSS
----
SCSS is required to compile SCSS duh.

Either install ``ruby`` and ``ruby-gems``, along with the ``sass`` gem, or if you’re using Arch, you can just install ``ruby-sass`` from the AUR.

Environment variables
---------------------

There’s a script in the root folder to make things easier.

::

  $ z-manage.py --help

It uses environment variables to know where everything is, so add the following to .bashrc:

::

  export ZOONAS_BROWSER=firefox
  export ZOONAS_TERM=xfce4-terminal
  export ZOONAS_SERVER_IP=''
  export ZOONAS_SERVER_USER=''
  export ZOONAS_VENV=~/.virtualenvs/zoonas
  export ZOONAS_RECAPTCHA_PUBLIC_KEY=''
  export ZOONAS_RECAPTCHA_PRIVATE_KEY=''
  export ZOONAS_EMBEDLY_KEY=''
  export ZOONAS_AWS_ACCESS_KEY_ID=''
  export ZOONAS_AWS_SECRET_ACCESS_KEY_ID=''
  export ZOONAS_AWS_STORAGE_BUCKET_NAME=''
  export ZOONAS_DB_NAME=''
  export ZOONAS_DB_USER=''
  export ZOONAS_DB_PASSWORD=''
  export ZOONAS_DJANGO_SECRET_KEY=''

And fill in the blanks.

To install the rest of the dependencies and create the database tables, you should type:

::

  $ z-manage.py --install

You can run the development server with:

::

  $ z-manage.py --run

Other stuff
-----------
To use SQLite, create a folder named db at the same level as the repository and leave the db environment variables undefined. Also, don’t use SQLite for this.
