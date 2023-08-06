=================================================================
fuggit: for when you just can't put that one annoying file in git
=================================================================

You know the feeling. You're making a quick dirty hack to a file on a
remote machine. The file isn't under version control. You want to have the
convenience of editing the file locally, *and* you want the ability to roll
back your changes. Putting the remote file under version control is just too
hard, so what do you say? fuggit.

Specifically::

    fuggit add remote.hostname.com/etc/file.name

this will grab ``/etc/file.name`` from the machine ``remote.hostname.com``; save it
as ``remote.hostname.com/etc/file.name`` under ``$PWD.`` The file will be added and
committed to git.

::

    fuggit pull remote.hostname/etc/file.name

can be used to refresh your local copy of the file. Any local changes
will be preserved; any remote changes will result in a new commit.

::

    fuggit vimdiff remote.hostname/etc/file.name

will open a vimdiff window showing your local working copy of the file and the
remote copy. Thanks to the magic of vim, any changes you make to the remote
file will be pushed to the servce once you close the file. Any local changes
will be left for you to commit as you see fit.

Installation
------------

Before you can use fuggit, you'll have to do a spot of basic setup.

You'll want to create a directory to use for your local history::

    mkdir localhistory
    cd localhistory
    git init .

You'll need to perform all fuggit commands from this directory. As you add
files you'll get one directory under this base for each host you're managing
files on.

You could install fuggit system-wide::

    sudo pip install fuggit

Or you could create a virtualenv inside your ``localhistory`` directory and
install it there::

    virtualenv .
    source bin/activate
    pip install fuggit
