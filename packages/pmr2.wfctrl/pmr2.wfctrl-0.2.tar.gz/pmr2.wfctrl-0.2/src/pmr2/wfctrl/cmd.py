import logging
from os.path import join
import sys

if sys.version_info > (3, 0): # pragma: no cover
    from configparser import ConfigParser
    from io import StringIO
else: # pragma: no cover
    from ConfigParser import ConfigParser
    # io.StringIO in python2.7 is not ready for the above.
    from StringIO import StringIO

from pmr2.wfctrl.core import BaseDvcsCmd, register_cmd
from pmr2.wfctrl.utils import set_url_cred

logger = logging.getLogger(__name__)


class DemoDvcsCmd(BaseDvcsCmd):

    binary = 'vcs'
    marker = '.marker'
    default_remote = '__default_remote__'
    _default_target = 'http://vcs.example.com/repo'

    def __init__(self, remote=None, queue=None):
        self.remote = remote
        self.queue = queue or []

    def clone(self, workspace, **kw):
        self.queue.append([self.binary, 'clone', self.remote,
            workspace.working_dir])

    def init_new(self, workspace, **kw):
        self.queue.append([self.binary, 'init', workspace.working_dir])

    def add(self, workspace, path, **kw):
        self.queue.append([self.binary, 'add', path])

    def commit(self, workspace, message, **kw):
        self.queue.append([self.binary, 'commit', '-m', message])

    def update_remote(self, workspace, target_remote=None, **kw):
        pass

    def read_remote(self, workspace, target_remote=None, **kw):
        return self.remote or self._default_target

    def pull(self, workspace, **kw):
        self.queue.append([self.binary, 'pull'])

    def push(self, workspace, **kw):
        self.queue.append([self.binary, 'push'])


class MercurialDvcsCmd(BaseDvcsCmd):

    cmd_binary = 'hg'
    name = 'mercurial'
    marker = '.hg'
    default_remote = 'default'
    _hgrc = 'hgrc'
    _committer = None

    def _args(self, workspace, *args):
        result = ['-R', workspace.working_dir]
        result.extend(args)
        return result

    def set_committer(self, name, email, **kw):
        # TODO persist config.
        self._committer = '%s <%s>' % (name, email)

    def clone(self, workspace, **kw):
        return self.execute('clone', self.remote, workspace.working_dir)

    def init_new(self, workspace, **kw):
        return self.execute('init', workspace.working_dir)

    def add(self, workspace, path, **kw):
        return self.execute(*self._args(workspace, 'add', path))

    def commit(self, workspace, message, **kw):
        # XXX need to customize the user name
        cmd = ['commit', '-m', message]
        if self._committer:
            cmd.extend(['-u', self._committer])
        return self.execute(*self._args(workspace, *cmd))

    def read_remote(self, workspace, target_remote=None, **kw):
        target_remote = target_remote or self.default_remote
        target = join(workspace.working_dir, self.marker, self._hgrc)
        cp = ConfigParser()
        cp.read(target)
        if cp.has_option('paths', target_remote):
            return cp.get('paths', target_remote)

    def write_remote(self, workspace, target_remote=None, **kw):
        target_remote = target_remote or self.default_remote
        target = join(workspace.working_dir, self.marker, self._hgrc)
        cp = ConfigParser()
        cp.read(target)
        if not cp.has_section('paths'):
            cp.add_section('paths')
        cp.set('paths', target_remote, self.remote)
        with open(target, 'w') as fd:
            cp.write(fd)

    def pull(self, workspace, username=None, password=None, **kw):
        # XXX origin may be undefined
        target = self.get_remote(workspace,
            username=username, password=password)
        # XXX assuming repo is clean
        args = self._args(workspace, 'pull', target)
        return self.execute(*args)

    def push(self, workspace, username=None, password=None, **kw):
        # XXX origin may be undefined
        push_target = self.get_remote(workspace,
            username=username, password=password)
        args = self._args(workspace, 'push', push_target)
        return self.execute(*args)

    def reset_to_remote(self, workspace, branch=None):
        if branch is None:
            branch = 'tip'
        args = self._args(workspace, 'update', '-C', '-r', branch)
        return self.execute(*args)


class GitDvcsCmd(BaseDvcsCmd):

    cmd_binary = 'git'
    name = 'git'
    marker = '.git'

    default_remote = 'origin'
    _committer = (None, None)

    def _args(self, workspace, *args):
        worktree = workspace.working_dir
        gitdir = join(worktree, self.marker)
        result = ['--git-dir=%s' % gitdir, '--work-tree=%s' % worktree]
        result.extend(args)
        return result

    def set_committer(self, name, email, **kw):
        self._committer = (name, email)

    def clone(self, workspace, **kw):
        return self.execute('clone', self.remote, workspace.working_dir)

    def init_new(self, workspace, **kw):
        return self.execute('init', workspace.working_dir)

    def add(self, workspace, path, **kw):
        return self.execute(*self._args(workspace, 'add', path))

    def commit(self, workspace, message, **kw):
        # XXX no temporary override as far as I know.
        name, email = self._committer
        if name:
            self.execute(*self._args(workspace, 'config', 'user.name', name))
        if email:
            self.execute(*self._args(workspace, 'config', 'user.email', email))
        return self.execute(*self._args(workspace, 'commit', '-m', message))

    def read_remote(self, workspace, target_remote=None, **kw):
        target_remote = target_remote or self.default_remote
        stdout, err = self.execute(*self._args(workspace, 'remote', '-v'))
        if stdout:
            for lines in stdout.splitlines():
                remotes = lines.decode('utf8', errors='replace').split()
                if remotes[0] == target_remote:
                    # XXX assuming first one is correct
                    return remotes[1]

    def write_remote(self, workspace, target_remote=None, **kw):
        target_remote = target_remote or self.default_remote
        stdout, err = self.execute(*self._args(workspace, 'remote',
            'rm', target_remote))
        stdout, err = self.execute(*self._args(workspace, 'remote',
            'add', target_remote, self.remote))

    def pull(self, workspace, username=None, password=None, **kw):
        # XXX origin may be undefined
        target = self.get_remote(workspace,
            username=username, password=password)
        # XXX assuming repo is clean
        args = self._args(workspace, 'pull', target)
        return self.execute(*args)

    def push(self, workspace, username=None, password=None, branches=None,
            **kw):
        """
        branches
            A list of branches to push.  Defaults to --all
        """

        push_target = self.get_remote(workspace,
            username=username, password=password)
        args = self._args(workspace, 'push', push_target)
        if not branches:
            args.append('--all')
        elif isinstance(branches, list):
            args.extend(branches)

        return self.execute(*args)

    def reset_to_remote(self, workspace, branch=None):
        # XXX not actually resetting to reomte
        # XXX assuming 'master' is the current branch
        if branch is None:
            branch = 'master'
        args = self._args(workspace, 'reset', '--hard', branch)
        return self.execute(*args)


def _register():
    register_cmd(MercurialDvcsCmd, GitDvcsCmd)

register = _register
register()
del register
