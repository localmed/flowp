from flowp.testing import Runner
from flowp.files import Watch
import argparse
import sys
import subprocess


def run():
    subprocess.call([sys.executable, '-m', 'flowp.testing'])


def rerun(filename, action):
    run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()

    if args.watch:
        run()
        Watch(['*.py', '**/*.py'], rerun).wait()
    else:
        Runner().run()
