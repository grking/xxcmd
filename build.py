#!/usr/bin/env python3
# build.py
# A build helper for xxcmd.
# This script is not required, it just speeds up a few routine
# developer tasks.
#
# This script by default:
#   1. Updates the latest command line options into the README
#   2. Updates the latest config options into the README
#   3. Generates a man page from docs/man.src.md
#   4. Updates the man page with the latest command line options
#   5. Runs the unit tests and coverage report
#   6. Builds a pypi package
#
# ./build.py clean
#   1. Deletes temporary files from the project directory
#
# ./build.py publish
#   1. Updates the version in the README badges
#   2. Updates the version and date in the CHANGELOG
#   3. Commits and pushes those two changes
#   4. Creates a git tag with the version and pushes it
#   5. Builds a pypi package
#   6. Publishes the pypi package to pypi.
#
# Requires:
#
#   OS Packages: help2man, pandoc
#   Pip packages: flit, pytest, pytest-cov
#
import re
import subprocess
import tempfile
import shutil
import os
import datetime
import sys
from xxcmd.config import Config
from xxcmd import __version__ as VERSION


# Replace some text in a text file
def replace(filename, starttag, endtag, content):

    # Open a temporary file
    outfilename = tempfile.mktemp()
    outfile = open(outfilename, "wt", encoding='utf-8')

    # Open the target file
    infile = open(filename, "rt", encoding='utf-8')

    # Iterate lines until our start tag
    skipline = False
    while True:

        line = infile.readline()
        if line == '':
            break

        if line.strip() == endtag and skipline:
            skipline = False
            # Inject new content
            outfile.write(content)

        if not skipline:
            outfile.write(line)

        if line.strip() == starttag:
            skipline = True

    # Clean up
    outfile.close()
    infile.close()

    # Copy the temp file
    shutil.copy(outfilename, filename)
    os.unlink(outfilename)


# Run a shell command
def run(cmd):
    exitcode = subprocess.call(cmd.split() if type(cmd) is str else cmd)
    if exitcode:
        exit(exitcode)


if __name__ == '__main__':

    # Clean up
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        for wipe in [
            'dist', '__pycache__', 'htmlcov', '.coverage', '.pytest_cache'
        ]:
            os.system('rm -rf {0}'.format(wipe))
        exit(0)

    # Publish
    if len(sys.argv) == 2 and sys.argv[1] == 'publish':

        # Ensure we can do a normal build first
        run('./build.py')

        # Update the README with our release version number
        infile = open("README.md", "rt", encoding='utf-8')
        lines = infile.readlines()
        infile.close()
        newline = re.sub('(v\d+\.\d+\.\d+)', 'v'+VERSION, lines[2])
        if newline == lines[2]:
            print("Could not update the readme version")
            exit(1)
        lines[2] = newline
        outfile = open("README.md", "wt", encoding='utf-8')
        outfile.writelines(lines)
        outfile.close()

        # Update the CHANGELOG with our release date and version
        infile = open("CHANGELOG.md", "rt", encoding='utf-8')
        lines = infile.readlines()
        infile.close()
        if 'unreleased' in lines[2].lower():
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            lines[2] = "## [{0}] - {1}\n".format(VERSION, today)
        else:
            print("Could not update the changelog")
            exit(1)
        outfile = open("CHANGELOG.md", "wt", encoding='utf-8')
        outfile.writelines(lines)
        outfile.close()
        # Git commit those doc changes, and any other possible ones
        run('git add README.md CHANGELOG.md docs/*')
        run('git commit -m'.split() + ['"Release v{0}"'.format(VERSION)])
        run('git push')
        # Git tag
        run('git tag v{0}'.format(VERSION))
        run('git push --tags')
        # Build pypi package
        run('flit build')
        run('flit publish')
        exit(0)

    # Update the README.md file with the latest command line help output
    result = subprocess.check_output('python -m xxcmd -h'.split())
    content = result.decode('utf-8')
    content = "\n```text\n" + content + "\n```\n"
    replace('README.md', '# Further Usage', '# Configuration', content)

    # Update README.md file with the latest config options
    # Generate all default config file values
    config = Config()
    filename = tempfile.mktemp()
    Config.DEFAULT_CONFIG_FILE = filename
    config.save()
    infile = open(filename, "rt")
    content = infile.read().strip()[8:] + "\n"
    infile.close()
    os.unlink(filename)
    # Update the README
    replace('README.md', '[xxcmd]', '```', content)

    # Rebuild the man page
    run('pandoc --standalone --to man docs/man.src.md -o docs/xx.1')

    # Grab the command line options in man page format
    filename = tempfile.mktemp()
    help2man = 'help2man -N -o {0}'.format(filename).split()
    help2man += ["python -m xxcmd"]
    run(help2man)
    # Grab content from our temporary man page
    infile = open(filename, "rt", encoding='utf-8')
    content = []
    while True:
        line = infile.readline()
        if line == '':
            break
        line = line.strip()
        if content:
            content.append(line)
        if line == '.SS "positional arguments:"':
            content.append(line)
    infile.close()
    os.unlink(filename)
    content = "\n".join(content)
    replace('docs/xx.1', '.SH OPTIONS', '.SH EXAMPLES', content)

    # Run tests
    run('pytest -q --cov-report term --cov-report html --cov=xxcmd tests/')
    # Build pypi package
    run('flit build')
