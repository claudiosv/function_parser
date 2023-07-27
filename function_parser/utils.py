import itertools
import os
import re
import subprocess
import tempfile
from typing import List, Tuple

import requests


def flatten(l):
    """Flatten list of lists.
    Args:
        l: A list of lists
    Returns: A flattened iterable
    """
    return itertools.chain.from_iterable(l)


def chunks(l: List, n: int):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def remap_nwo(nwo: str) -> Tuple[str, str]:
    r = requests.get('https://github.com/{}'.format(nwo))
    if r.status_code not in (404, 451, 502): # DMCA
        if 'migrated' not in r.text:
            if r.history:
                return (nwo, '/'.join(re.findall(r'"https://github.com/.+"', r.history[0].text)[0].strip('"').split('/')[-2:]))
            return (nwo, nwo)
    return (nwo, None)


def get_sha(proj_dir: str):
    curr_dir = os.getcwd()
    os.chdir(proj_dir)
    # git rev-parse HEAD
    cmd = ['git', 'rev-parse', 'HEAD']
    sha = subprocess.check_output(cmd).strip().decode('utf-8')
    os.chdir(curr_dir)
    return sha

def get_nwo(proj_dir: str):
    curr_dir = os.getcwd()
    os.chdir(proj_dir)
    # Run the git command
    cmd = ['git', 'config', '--local', '--get', 'remote.origin.url']
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.chdir(curr_dir)

    # Check for errors
    if result.returncode != 0:
        print(f'Error: {result.stderr}')
        return None

    # Extract the username and repo
    url = result.stdout.strip()

    # Check if URL is in SSH format
    ssh_match = re.search('git@github\.com:(.*)\.git', url)

    # If URL is in SSH format, return the matched group
    if ssh_match is not None:
        return ssh_match.group(1)

    # If URL is in HTTPS format, return the matched group
    https_match = re.search('https://github\.com/(.*)\.git', url)
    if https_match is not None:
        return https_match.group(1)

    # If no match was found, print an error and return None
    print(f'Error: Unexpected URL format: {url}')
    return None

def download(nwo: str):
    os.environ['GIT_TERMINAL_PROMPT'] = '0'
    tmp_dir = tempfile.TemporaryDirectory()
    cmd = ['git', 'clone', '--depth=1', 'https://github.com/{}.git'.format(nwo), '{}/{}'.format(tmp_dir.name, nwo)]
    subprocess.run(cmd, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    return tmp_dir


def walk(tmp_dir: tempfile.TemporaryDirectory, ext: str):
    results = []
    for root, _, files in os.walk(tmp_dir):
        for f in files:
            if f.endswith('.' + ext):
                results.append(os.path.join(root, f))
    return results