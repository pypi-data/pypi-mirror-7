====
Info
====

Upload snapshots of a revision to one or more FTP server.

It will upload all files of a revision and set a (local) tag like
``uploaded@host``. If it will find an existing tag for that host it
will remove vanished files and upload only the difference between
that revision and the new one.

-----
Notes
-----

If an error happens on server-side on deleting or CHMODing a file
it will only print a warning about that but it will abort if it can't
upload a files or create a directory.
Since Mercurial doesn't track directories it won't delete existing
directories on server even there is no file anymore.

---------
Important
---------

This is **not** a command for push/pull over ftp!


====
hgrc
====

-----------
``[paths]``
-----------

You can add multiple destinations to ``[paths]`` like in push/pull::

    [paths]
        ftp    = ftp://[user[:pass]@]host[:port]/[path]
        myhost = ftp://andre@incubo.de/htdocs

* You can select it like: ``hg ftp myhost``
* Or you can provide a complete URL: ``hg ftp ftp://user:psw@host/basedir``

If you don't provide a ``destination`` commandline argument, hgftp will use ``ftp`` in ``[paths]`` by default.

If your username contains an ``@`` character, encode it as ``%40`` to avoid confusing Python's ``urlsplit()`` function.

---------
``[ftp]``
---------

If you add ``chmod_file`` or ``chmod_dir`` it will ``CHMOD`` it on upload. If there is no option for chmod the extension won't call ``SITE CHMOD`` on ftp server.

::

    [ftp]
        chmod_file  = 644
        chmod_dir   = 755
        global_tags = False
        prefix_tags = uploaded@


=======
Options
=======

There are some options that can overwrite settings in your hgrc::

    -a --all     upload all files of a changeset; do not use the difference
    -d --dir     CHMOD new directories to given mode
    -f --file    CHMOD new/changed files to given mode
    -g --global  make the tag global
    -o --only    only upload or remove files; do not set a tag
    -r --rev     revision that will be uploaded
    -s --show    show files that will be uploaded or deleted
    -t --tag     use another tag name
    -u --upload  start uploading or removing changed files

The extension will only start uploading / removing your files if you provide ``--upload`` as an option. A tag will only be set if upload was successful.

If ``--rev`` is not provided it will use the current revision of your working dir. But it won't use uncommitted changes of that working dir. There will be no prefix if you use ``--tag``!


========
Use Case
========

My use case for this plugin is to manage uploads of websites. If you have your website (.html, .php, etc.) under mercurial control you can easily upload snapshots to your provider. If you change something on your site you only need to upload the difference of the last uploaded snapshot and the current/selected revision without to do it yourself.

1. Add your website files to mercurial
2. Upload initial snapshot to ftp server (set ``uploaded@host`` tag)
3. Do many commits to your website files
4. Upload only new/changed files to your last uploaded snapshot (and remove vanished files)

Really useful if you use a modified version of existing open source wikis/forums/cms and wants to be in sync with upstream changes.

Just commit upstream changes to branch ``vanilla`` and your modified version will be in ``default``. So you can merge it on new upstream versions and use this extension to upload your synced snapshot.
