from distutils.core import setup
import os

data = [
       ('/usr/share/zsh/site-functions', ['cheat/autocompletion/_cheat.zsh']),
       ('/etc/bash_completion.d'       , ['cheat/autocompletion/cheat.bash']),
       ('/usr/share/fish/completions'  , ['cheat/autocompletion/cheat.fish'])
       ]

if os.name == 'nt':
    data = []

setup(
    name         = 'cheat',
    version      = '2.0.5',
    author       = 'Chris Lane',
    author_email = 'chris@chris-allen-lane.com',
    license      = 'GPL3',
    description  = 'cheat allows you to create and view interactive cheatsheets '
    'on the command-line. It was designed to help remind *nix system '
    'administrators of options for commands that they use frequently, but not '
    'frequently enough to remember.',
    url          = 'https://github.com/chrisallenlane/cheat',
    packages     = [
        'cheat',
        'cheat.cheatsheets',
        'cheat.test',
    ],
    package_data = {
        'cheat.cheatsheets': [f for f in os.listdir('cheat/cheatsheets') if '.' not in f]
    },
    scripts      = ['bin/cheat'],
    data_files   = data,
    install_requires = [
        'docopt >= 0.6.1',
        'pygments >= 1.6.0',
    ]
)
