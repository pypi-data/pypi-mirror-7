import os
import subprocess


def handler(page):
    if page == 'index':
        subprocess.Popen(os.path.dirname(__file__) + '/doc/_build/html/index.html', shell=True)
    elif page == 'git':
        subprocess.Popen(os.path.dirname(__file__) + '/doc/_build/html/git.html', shell=True)
