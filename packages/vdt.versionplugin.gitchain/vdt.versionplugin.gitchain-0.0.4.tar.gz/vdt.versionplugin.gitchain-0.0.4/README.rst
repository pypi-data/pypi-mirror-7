vdt.versionplugin.gitchain
==========================

Instead of building packages as a freezed state, propagate tags between git repositories.

Example of pushing::

    version --plugin=gitchain --target-repo=file:///tmp/vdt.versionplugin.gitchain --target-ref=refs/heads/kakalkal --force -v
    DEBUG:vdt.versionplugin.default:Extra argument are ['--target-repo=file:///tmp/vdt.versionplugin.gitchain', '--target-ref=refs/heads/kakalkal', '--force']
    WARNING:vdt.versionplugin.default:Not tagging, this revision is already tagged as: 0.0.1

    DEBUG:vdt.versionplugin.gitchain.freeze:Arguments are Namespace(force=True, target_ref='refs/heads/kakalkal', target_repo='file:///tmp/vdt.versionplugin.gitchain')
    DEBUG:vdt.versionplugin.gitchain.freeze:Building version 0.0.1 with gitchain.
    Note: checking out '0.0.1'.

    You are in 'detached HEAD' state. You can look around, make experimental
    changes and commit them, and you can discard any commits you make in this
    state without impacting any branches by performing another checkout.

    If you want to create a new branch to retain commits you create, you may
    do so (now or later) by using -b with the checkout command again. Example:

      git checkout -b new_branch_name

    HEAD is now at a3b304b... Parse arguments.
    DEBUG:vdt.version.shared:M	vdt/versionplugin/gitchain/freeze.py
    M	vdt/versionplugin/gitchain/shared.py

Example of tagging and then pushing::

    version --plugin=gitchain --target-repo=file:///tmp/vdt.versionplugin.gitchain --target-ref=refs/heads/kakalkal --force -v -p
    DEBUG:vdt.versionplugin.default:Extra argument are ['--target-repo=file:///tmp/vdt.versionplugin.gitchain', '--target-ref=refs/heads/kakalkal', '--force']
    DEBUG:vdt.versionplugin.default:Writing version 0.0.2
    DEBUG:vdt.versionplugin.gitchain.freeze:Arguments are Namespace(force=True, target_ref='refs/heads/kakalkal', target_repo='file:///tmp/vdt.versionplugin.gitchain')
    DEBUG:vdt.versionplugin.gitchain.freeze:Building version 0.0.2 with gitchain.
    Note: checking out '0.0.2'.

    You are in 'detached HEAD' state. You can look around, make experimental
    changes and commit them, and you can discard any commits you make in this
    state without impacting any branches by performing another checkout.

    If you want to create a new branch to retain commits you create, you may
    do so (now or later) by using -b with the checkout command again. Example:

      git checkout -b new_branch_name

    HEAD is now at a4530fe... Improved readme.
    DEBUG:vdt.version.shared:
    DEBUG:vdt.versionplugin.gitchain.freeze:Running command git push --force file:///tmp/vdt.versionplugin.gitchain HEAD:refs/heads/kakalkal
    Counting objects: 16, done.
    Delta compression using up to 2 threads.
    Compressing objects: 100% (10/10), done.
    Writing objects: 100% (10/10), 1.71 KiB | 0 bytes/s, done.
    Total 10 (delta 4), reused 0 (delta 0)
    To file:///tmp/vdt.versionplugin.gitchain
       a3b304b..a4530fe  HEAD -> kakalkal
    DEBUG:vdt.versionplugin.gitchain.freeze:
    Switched to branch 'master'
    DEBUG:vdt.version.shared:0

Example of pushing tags as well::

    version --plugin=gitchain --target-repo=file:///tmp/vdt.versionplugin.gitchain --target-ref=refs/heads/kakalkal --force -v -p --tags
    DEBUG:vdt.versionplugin.default:Extra argument are ['--target-repo=file:///tmp/vdt.versionplugin.gitchain', '--target-ref=refs/heads/kakalkal', '--force', '--tags']
    DEBUG:vdt.versionplugin.default:Writing version 0.0.4
    DEBUG:vdt.versionplugin.gitchain.freeze:Arguments are Namespace(force=True, tags=True, target_ref='refs/heads/kakalkal', target_repo='file:///tmp/vdt.versionplugin.gitchain')
    DEBUG:vdt.versionplugin.gitchain.freeze:Building version 0.0.4 with gitchain.
    Note: checking out '0.0.4'.

    You are in 'detached HEAD' state. You can look around, make experimental
    changes and commit them, and you can discard any commits you make in this
    state without impacting any branches by performing another checkout.

    If you want to create a new branch to retain commits you create, you may
    do so (now or later) by using -b with the checkout command again. Example:

      git checkout -b new_branch_name

    HEAD is now at a8a87b6... Added option to push tags as well.
    DEBUG:vdt.version.shared:
    DEBUG:vdt.versionplugin.gitchain.freeze:Running command git push --force --tags file:///tmp/vdt.versionplugin.gitchain HEAD:refs/heads/kakalkal
    Counting objects: 15, done.
    Delta compression using up to 2 threads.
    Compressing objects: 100% (8/8), done.
    Writing objects: 100% (8/8), 814 bytes | 0 bytes/s, done.
    Total 8 (delta 4), reused 0 (delta 0)
    To file:///tmp/vdt.versionplugin.gitchain
       48d1389..a8a87b6  HEAD -> kakalkal
     * [new tag]         0.0.4 -> 0.0.4
    DEBUG:vdt.versionplugin.gitchain.freeze:
    Switched to branch 'master'
    Your branch is ahead of 'origin/master' by 1 commit.
      (use "git push" to publish your local commits)
    DEBUG:vdt.version.shared:0
