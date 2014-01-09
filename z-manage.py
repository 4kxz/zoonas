#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
import time


SELF = sys.argv[0]
BROWSER = os.getenv('ZOONAS_BROWSER', 'exo-open')
TERMINAL = os.getenv('ZOONAS_TERM', 'xterm')
VIRTUALENV = os.getenv('ZOONAS_VENV', './virtualenv')
VENVPIP = VIRTUALENV + '/bin/pip'
VENVPYTHON = VIRTUALENV + '/bin/python'
VENVSPHINX = VIRTUALENV + '/bin/sphinx-build'
VENVAPIDOC = VIRTUALENV + '/bin/sphinx-apidoc'
VENVCOVERAGE = VIRTUALENV + '/bin/coverage'
USER = os.getenv('ZOONAS_SERVER_USER', 'root')  # Safe default LOL.
SERVER = os.getenv('ZOONAS_SERVER_IP', '0.0.0.0')  # Not even trying.
SETTINGS = os.getenv('ZOONAS_SETTINGS_MODULE', 'settings.development')

# Let's be honest, I don't know what I'm doing.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.development')


COLOR = {'k': '\033[90m', 'r': '\033[91m', 'g': '\033[92m', 'y': '\033[93m',
         'b': '\033[94m', 'm': '\033[95m', 'c': '\033[96m', 'w': '\033[0m'}


def message(msg, color='g'):
    """Nicely colored message."""
    print(COLOR[color] + "[zoonas] {}".format(msg) + COLOR['w'])


def execute(cmd):
    """Execute command in current terminal."""
    p = subprocess.Popen(cmd)
    os.waitpid(p.pid, 0)[1]


def execterm(cmd, shell=True, title="Development"):
    """Execute command in a new terminal."""
    message("new terminal {}".format(title), 'b')
    cmd = "bash -i -c '{}'".format(cmd) if shell else cmd
    args = [TERMINAL,
            '--title="{}"'.format(title),
            '--command="{}"'.format(cmd)]
    os.system(' '.join(args))


def execsalt(args):
    """Sends salt command to everyone."""
    message("salt '*' " + ' '.join(args), 'c')
    command = ['sudo', 'salt', '-t', '20', '*'] + args
    p = subprocess.Popen(command)
    os.waitpid(p.pid, 0)[1]


def manage(args):
    """Moves to the django directory and runs manage.py with
    the arguments passed, using the virtualenv specified by the
    ZOONAS_VENV environment variable.
    """
    message("manage.py " + ' '.join(args), 'y')
    command = [VENVPYTHON, 'manage.py'] + args
    os.chdir('django')
    p = subprocess.Popen(command)
    os.waitpid(p.pid, 0)[1]
    os.chdir('..')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--browser',
                        action='store_true',
                        help="open development server in browser")
    parser.add_argument('-d', '--documentation',
                        action='store_true',
                        help="generate documentation with Sphinx")
    parser.add_argument('-dbs', '--syncdb',
                        action='store_true',
                        help="synchronise database")
    parser.add_argument('-lg', '--locale',
                        action='store_true',
                        help="generate locale files for translating")
    parser.add_argument('-lt', '--translate',
                        action='store_true',
                        help="generate translation from locale files")
    parser.add_argument('-m', '--manage',
                        nargs='+',
                        help="passes arguments to manage.py")
    parser.add_argument('-pi', '--pip-install',
                        nargs='+',
                        help="pip install/upgrade")
    parser.add_argument('-pf', '--pip-freeze',
                        action='store_true',
                        help="pip freeze")
    parser.add_argument('-r', '--runserver',
                        action='store_true',
                        help="run development server")
    parser.add_argument('-s', '--salt',
                        nargs='+',
                        help="send salt command to EVERYONE"
                        " (http://youtu.be/MrTsuvykUZk)")
    parser.add_argument('-sp', '--push',
                        action='store_true',
                        help="push current state to server")
    parser.add_argument('-t', '--test',
                        action='store_true',
                        help="run unit test")
    parser.add_argument('-tc', '--coverage',
                        action='store_true',
                        help="run unit test and generate coverage report")
    parser.add_argument('-z', '--ssh',
                        action='store_true',
                        help="ssh to server in new terminal")
    args = parser.parse_args()

    if args.browser:
        execute([BROWSER, 'http://localhost:8080'])

    if args.coverage:
        message("Running tests")
        os.chdir('django')
        execute([VENVCOVERAGE, 'run', 'manage.py', 'test', '-v', '2'])
        message("Generating report")
        execute([VENVCOVERAGE, 'html'])
        os.chdir('..')
        message("Done")
        message("The report should be available at django/htmlcov/index.html")

    if args.documentation:
        execute([VENVAPIDOC, '-o', 'doc', 'django'])
        os.chdir('doc')
        execute(['make', 'html', 'SPHINXBUILD={}'.format(VENVSPHINX)])
        os.chdir('..')

    if args.locale:
        manage(['makemessages', '-l', 'es_ES'])

    if args.manage is not None:
        manage(args.manage)

    if args.pip_install is not None:
        message("Piping...")
        execute([VENVPIP, 'install', '-U'] + args.pip_install)

    if args.pip_freeze:
        execute([VENVPIP, 'freeze'])

    if args.push:
        message("Compiling scss")
        execute(['mkdir', '-p', '.tmp'])
        execute(['scss',
                 'static/scss/style.scss:.tmp/style.css',
                 '--style',
                 'compressed',
                 ])
        message("Generating translation")
        execute([SELF, '-m', 'compilemessages'])
        message("Collecting static content")
        execute([SELF, '-m', 'collectstatic'])
        message("Pushing state to server")
        execsalt(["saltutil.refresh_pillar"])
        execsalt(['state.highstate'])

    if args.runserver:
        message("Starting scss watch")
        execute(['mkdir', '-p', '.tmp'])
        execterm('scss --watch static/scss/style.scss:.tmp/style.css',
                 title="SCSS")
        message("Starting redis")
        execterm('redis-server',
                 title="Redis", shell=False)
        message("Starting celery")
        execterm('{} -m celery worker'.format(SELF),
                 title="Celery")
        message("Starting django")
        execterm('{} -m runserver 0.0.0.0:8080'.format(SELF),
                 title="Django")
        message("Starting postgres, should be waiting for password")
        execterm("sudo -u postgres sh -c 'cd /home/postgres; postgres -D 9.3'",
                 title='Postgres', shell=False)

    if args.salt is not None:
        execsalt(args.salt)

    if args.ssh:
        command = 'ssh {}@{}'.format(USER, SERVER)
        execterm(command, title=command)

    if args.syncdb:
        manage(['syncdb'])

    if args.test:
        manage([
            'test',
            'users',
            'zones',
            'submissions',
            'domains',
            'votes',
            'notes',
            ])

    if args.translate:
        manage(['compilemessages'])
