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

Features
---------

* Work fine with initial commit.
* Work fine with all filenames.
* Work with index contents instead of working copy.
* Plugin architecture: adding new checks is easy.
* Builtin plugins for:

  * validate json files
  * validate Python-code with
    `flake8 <https://pypi.python.org/pypi/flake8/>`_
    (
    `mccabe plugin <https://pypi.python.org/pypi/mccabe/>`_
    is enabled
    )
    and
    `pep8-naming <https://pypi.python.org/pypi/pep8-naming/>`_
  * validate .rst files with
    `restructuredtext_lint <https://pypi.python.org/pypi/restructuredtext_lint>`_
  * validate .yaml files with `PyYAML <https://pypi.python.org/pypi/PyYAML>`_
  * check filesize

Examples
--------

Install hook to current Git-repository::

  git-pre-commit-hook install \
    --plugin flake8 \
    --plugin json \
    --plugin file_size \
    --plugin rst \
    --plugin yaml

Installed hook rejects commits:

* if any file has size greater than 10MB
* if files with .json extension contains invalid JSON
* if Python-code doesn't pass check with flake8 (with pep8-naming)
* if files with .rst extension contains invalid RST
* if files with .yaml extension contains invalid YAML

List available plugins::

  git-pre-commit-hook list-plugins

Show information about plugin::

  git-pre-commit-hook show-plugin-info json


Links
-----

* `Fork me on GitHub <https://github.com/evvers/git-pre-commit-hook>`_
