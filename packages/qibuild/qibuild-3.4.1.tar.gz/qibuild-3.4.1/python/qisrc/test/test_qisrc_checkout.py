import os

import qisrc.git
from qisrc.test.conftest import TestGitWorkTree

def test_checkout_happy(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("manifest", "--add", "default", manifest_url)
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("checkout", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = qisrc.git.Git(foo_proj.path)
    assert foo_git.get_current_branch() == "devel"
    bar_proj = git_worktree.get_git_project("bar")
    bar_git = qisrc.git.Git(bar_proj.path)
    assert bar_git.get_current_branch() == "master"

def test_checkout_preserve_changes_when_checkout_fails(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "README.txt", "readme\n")
    qisrc_action("manifest", "--add", "default", manifest_url)
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    readme = os.path.join(foo_proj.path, "README.txt")
    with open(readme, "w") as fp:
        fp.write("unstaged\n")
    qisrc_action("checkout", "devel")
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = qisrc.git.Git(foo_proj.path)
    assert foo_git.get_current_branch() == "master"
    # With --force:
    qisrc_action("checkout", "devel", "--force")
    assert foo_git.get_current_branch() == "devel"
