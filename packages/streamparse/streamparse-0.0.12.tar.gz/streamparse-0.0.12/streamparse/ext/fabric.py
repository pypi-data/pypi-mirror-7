"""streamparse.ext.fabric

fabric tasks that are imported into a project's fabfile.py.

Should be used like this::

    from fabric.api import *
    from streamparse.ext.fabric import *

    # your other tasks
"""
from __future__ import absolute_import, print_function

import os

from fabric.api import *
from fabric.contrib.files import exists

from .util import get_env_config


__all__ = ["activate_env", "create_or_update_virtualenvs", "tail_logs"]


@task
def _tail_logs(pattern=None):
    # list log files found
    ls_cmd = "cd {log_path} && ls".format(log_path=env.log_path)
    if pattern is not None:
        ls_cmd += " | egrep '{pattern}'".format(
            pattern=pattern)
    run(ls_cmd)
    # tail -f all of them
    tail_pipe = " | xargs tail -f"
    run(ls_cmd + tail_pipe)

@task
def tail_logs(pattern=None):
    """Follow (tail -f) the log files on remote Storm workers.

    Will use the `log_path` and `workers` properties from config.json.
    """
    execute(_tail_logs, pattern, hosts=env.storm_workers)

@task
def activate_env(env_name=None):
    """Activate a particular environment from a streamparse project's
    config.json file and populatefabric's env dictionary with appropriate
    values.

    :param env_name: a `str` corresponding to the key within the config file's
    "envs" dictionary.
    """
    env_name, env_config = get_env_config(env_name)

    # get the host only (not port) for Nimbus since we'll be using SSH anyway
    # env.storm_nimbus = [env_config["nimbus"].split(":")[0]]
    env.storm_workers = env_config["workers"]
    env.user = env_config["user"]
    env.log_path = env_config["log_path"]
    env.virtualenv_root = env_config["virtualenv_root"]
    env.disable_known_hosts = True
    env.forward_agent = True


@parallel
def _create_or_update_virtualenv(virtualenv_root,
                                 virtualenv_name,
                                 requirements_file):
    virtualenv_path = os.path.join(virtualenv_root, virtualenv_name)
    if not exists(virtualenv_path):
        puts("virtualenv not found in {}, creating one.".format(virtualenv_root))
        run("virtualenv {}".format(virtualenv_path))

    puts("Uploading requirements.txt to temporary file.")
    tmpfile = run("mktemp /tmp/streamparse_requirements-XXXXXXXXX.txt")
    put(requirements_file, tmpfile)

    puts("Updating virtualenv: {}".format(virtualenv_name))
    cmd = "source {}".format(os.path.join(virtualenv_path, 'bin/activate'))
    with prefix(cmd):
        run("pip install streamparse")
        run("pip install -r {}".format(tmpfile))

    run("rm {}".format(tmpfile))


@task
def create_or_update_virtualenvs(virtualenv_name, requirements_file):
    """Create or update virtualenvs on remote servers.

    Assumes that virtualenv is on the path of the remote server(s).

    :param virtualenv_name: the name of the virtualenv.
    :param requirements_file: path to the requirements.txt file to use
    to update/install this virtualenv.
    """
    execute(_create_or_update_virtualenv,
            env.virtualenv_root,
            virtualenv_name,
            requirements_file,
            hosts=env.storm_workers)
