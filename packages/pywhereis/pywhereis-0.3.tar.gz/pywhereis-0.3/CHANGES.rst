CHANGES
=======

0.3
---

- Fixing bug _issue#2: https://bitbucket.org/mouad/pywhereis/issue/2, This mean that
  user can install pywhereis once in any Python version, and use it everywhere i.e.
  with other python versions or inside virtualenv ... , This work for now with
  only POSIX compliant system.
- BUGFIX: Fix locating not pure Python modules, bug noticed when trying to
  locate lxml.etree.XPath.
- Add support to Python3.4 and Python3.3.
- Change versioning instead of 0.0.2 now it's 0.3.
- **Backward incompatibilty change**: pywhereis return now the real path instead of symlink.

0.0.2
-----

- Add support to locating zip archive and eggs modules.
- Add a new argument -s, --site-packages that enable looking in
  site-packages directory before current directory.
- BUGFIX: Fix ``whereis.resolve`` to always raise ImportError even if the
  module that we are searching for is broken (SyntaxError ...), the same
  with ``whereis.locate``.

0.0.1
-----

First release.
