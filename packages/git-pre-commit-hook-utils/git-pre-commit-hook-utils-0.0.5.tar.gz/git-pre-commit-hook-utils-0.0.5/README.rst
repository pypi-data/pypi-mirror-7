git-pre-commit-hook-utils
=========================

git-pre-commit-hook-utils is utils for implemeting Git pre-commit
hooks

Installation
------------

You can install, upgrade, uninstall git-pre-commit-hook-utils
with these commands::

  $ pip install git-pre-commit-hook-utils
  $ pip install --upgrade git-pre-commit-hook-utils
  $ pip uninstall git-pre-commit-hook-utils

Features:
---------

* Work fine with initial commit
* Work fine with all filenames
* Work with index contents instead of working copy

Examples
--------

Hook that reject commits with "big (>10Mib)" files::

  import sys
  import git_pre_commit_hook_utils

  for file_for_commit in git_pre_commit_hook_utils.files_staged_for_commit():
      if file_for_commit.size > 10 * 1024 * 1024:
          sys.exit(1)
  sys.exit(0)


Hook that reject invalid json files::

  import sys
  import json
  import git_pre_commit_hook_utils

  for file_for_commit in git_pre_commit_hook_utils.files_staged_for_commit():
    if file_for_commit.path.endswith('.json')
        try:
            json.loads(file_for_commit.contents)
        except Exception:
            sys.exit(1)
        else:
            sys.exit(0)


Links
-----

* `Fork me on GitHub <https://github.com/evvers/git-pre-commit-hook-utils>`_
