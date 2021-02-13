#!/usr/bin/env python3
# build.py
# A build helper for xxcmd.
# This script is not required, it just speeds up a few routine
# developer tasks.
#
# This script by default:
#   1. Updates the latest command line options into the README
#   2. Updates the latest config options into the README
#   3. Rebuilds the man page
#   4. Runs the unit tests and coverage report
#   5. Builds a pypi package
#
# ./build.py clean
#   1. Deletes temporary files from the project directory
#
# ./build.py publish-pypi
#   1. Updates the version in the README badges
#   2. Updates the version and date in the CHANGELOG
#   3. Commits and pushes those two changes
#   4. Creates a git tag with the version and pushes it
#   5. Builds a pypi package
#   6. Publishes the pypi package to pypi.
#
# ./build.py publish-arch
#   1. Updates the version number in the PKGBUILD
#   2. Updates the source hashes in the PKGBUILD
#   3. Update .SRCINFO
#   4. Builds the Arch package
#
# Requires:
#
#   OS Packages: help2man
#   Pip packages: flit, pytest, pytest-cov
#
# Arch Package Publishing Requires:
#
#   OS Packages: pacman-contrib
#
import re
import subprocess
import tempfile
import shutil
import datetime
import os
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


# Replace a version number in a line of a file
def replace_version(filename, linenum):

    infile = open(filename, "rt", encoding='utf-8')
    lines = infile.readlines()
    infile.close()
    newline = re.sub(r'(v\d+\.\d+\.\d+)', 'v'+VERSION, lines[linenum])
    if newline == lines[linenum]:
        newline = re.sub(r'(\d+\.\d+\.\d+)', VERSION, lines[linenum])
    if newline == lines[linenum]:
        ver = "[{0}] - {1}".format(
            VERSION, datetime.datetime.now().strftime('%Y-%m-%d'))
        newline = re.sub(r'Unreleased', ver, lines[linenum])
    if newline == lines[linenum]:
        print("Could not update the version in file {0}".format(filename))
        exit(1)
    lines[linenum] = newline
    outfile = open(filename, "wt", encoding='utf-8')
    outfile.writelines(lines)
    outfile.close()


# Run a shell command
def run(cmd):
    exitcode = subprocess.call(cmd.split() if type(cmd) is str else cmd)
    if exitcode:
        exit(exitcode)


if __name__ == '__main__':

    # Clean up
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        for wipe in [
            'dist', '__pycache__', 'htmlcov', '.coverage',
            '.pytest_cache', 'xxcmd/__pycache__', 'tests/__pycache__',
            'pkg', 'src', '*.zst', '*.tar.gz', '.SRCINFO'
        ]:
            os.system('rm -rf {0}'.format(wipe))
        exit(0)

    # PyPi Publish
    if len(sys.argv) == 2 and sys.argv[1] == 'publish-pypi':

        # Ensure we can do a normal build first
        run('./build.py')

        # Update the README with our release version number
        replace_version('README.md', 2)

        # Update the CHANGELOG with our release date and version
        replace_version('CHANGELOG.md', 2)

        # Git commit those doc changes, and any other possible ones
        run('git add README.md CHANGELOG.md docs/*')
        run('git commit -m'.split() + ['"Release v{0}"'.format(VERSION)])
        run('git push')
        # Git tag
        run('git tag v{0}'.format(VERSION))
        run('git push --tags')
        # Build pypi package
        run('flit build')
        #run('flit publish')
        exit(0)

    # Arch Publish
    if len(sys.argv) == 2 and sys.argv[1] == 'publish-arch':

        # Update Arch PKGBUILD with our release version
        replace_version('PKGBUILD', 2)

        # Update hashes in PKGBUILD
        run('updpkgsums')

        # Update SRCINFO
        run('makepkg --printsrcinfo > .SRCINFO')

        # Build Arch package
        run('makepkg')

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
    run(['help2man', '-i', 'docs/xx.h2m', '-n', "remembers other shell commands, "
         "so you don't have to.", '-o', 'docs/xx.1', '-N', "python -m xxcmd"])

    # Run tests
    run('pytest -q --cov-report term --cov-report html --cov=xxcmd tests/')
    # Build pypi package
    run('flit build')
