# build.py
# A build helper for xxcmd.
#
# This script:
#   1. Updates the latest command line options into the README
#   2. Updates the latest config options into the README
#   3. Generates a man page from docs/man.src.md
#   4. Updates the man page with the latest command line options
#   5. Runs the unit tests and coverage report
#   6. Builds a pypi package
#
# Requires:
#
#   OS Packages: help2man, pandoc
#   Pip packages: flit, coverage
#
import subprocess
import tempfile
import shutil
import os
from xxcmd.config import Config


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


if __name__ == '__main__':

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
    exitcode = subprocess.call('pandoc --standalone --to man docs/man.src.md -o docs/xx.1'.split())
    if exitcode:
        print("Man page build failed.")
        exit(exitcode)

    # Grab the command line options in man page format
    filename = tempfile.mktemp()
    help2man = f'help2man -N -o {filename}'.split()
    help2man += ["python -m xxcmd"]
    exitcode = subprocess.call(help2man)
    if exitcode:
        exit(exitcode)
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

    # Run tests and coverage report
    exitcode = subprocess.call('coverage run --source=. -m unittest discover'.split())
    if exitcode:
        exit(exitcode)
    exitcode = subprocess.call('python -m coverage report'.split())
    if exitcode:
        exit(exitcode)
    exitcode = subprocess.call('python -m coverage html'.split())
    if exitcode:
        exit(exitcode)

    # Build pypi package
    exitcode = subprocess.call('flit build'.split())
    if exitcode:
        exit(exitcode)
