git-pre-commit-hook
===================

git-pre-commit-hook - pre-commit hook for Git.

Installation
------------

You can install, upgrade, uninstall git-pre-commit-hook
with these commands::

  $ pip install git-pre-commit-hook
  $ pip install --upgrade git-pre-commit-hook
  $ pip uninstall git-pre-commit-hook

Features:
---------

* Work fine with initial commit.
* Work fine with all filenames.
* Work with index contents instead of working copy.
* Plugin architecture: adding new checks is easy.
* Builtin plugins for:
  * validate json files
  * validate files with flake8
  * check filesize

Examples
--------

Install hook to current Git-repository::

  git-pre-commit-hook install --plugin flake8 --plugin json --plugin file_size

Installed hook rejects commits:
* if any file has size greater than 10MB
* if files with .json extension contains invalid JSON
* if Python-code doesn't pass check with flake8

List available plugins::

  git-pre-commit-hook list-plugins

Show information about plugin::

  git-pre-commit-hook show-plugin-info json


Links
-----

* `Fork me on GitHub <https://github.com/evvers/git-pre-commit-hook>`_
