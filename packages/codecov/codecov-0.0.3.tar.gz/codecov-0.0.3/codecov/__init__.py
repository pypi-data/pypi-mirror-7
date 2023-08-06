import re
import os
import sys
import commands
import requests
import argparse
from json import dumps
from xml.dom.minidom import parseString

version = VERSION = __version__ = '0.0.3'


def generate_report(path):
    try:
        with open(path, 'r') as f:
            return generate_json(f.read())
    except:
        try:
            commands.getstatusoutput('coverage xml')
        except:
            return None
        else:
            with open(path, 'r') as f:
                return generate_json(f.read())

def generate_json(xml):
    coverage = parseString(xml).getElementsByTagName('coverage')[0]
    for package in coverage.getElementsByTagName('package'):
        if package.getAttribute('name') == '':
            files = dict([clazz(_class) for _class in coverage.getElementsByTagName('class')])
            branches = sum(map(lambda f: f['b'], files.values()))
            run = sum(map(lambda f: f['r'], files.values()))
            missing = sum(map(lambda f: f['m'], files.values()))
            excluded = 0 # not sure how to get this value
            partial = sum(map(lambda f: f['p'], files.values()))
            return {
                "branch-rate": coverage.getAttribute('branch-rate'),
                "timestamp": coverage.getAttribute('timestamp'),
                "version": coverage.getAttribute('version'),
                "line-rate": coverage.getAttribute('line-rate'),
                "totals": {
                    "b": branches,
                    "r": run,
                    "m": missing,
                    "e": excluded,
                    "p": partial,
                    "s": sum([run, missing, partial]),
                    "cov": ("%d" % int(round(float(run)/float(run+missing+partial)*100))) if run else "0"
                },
                "files": files
            }

def clazz(_class):
    # available: branch
    lines = map(lambda line: dict([(attr[0], line.getAttribute(attr)) for attr in ('number', 'condition-coverage', 'hits')]), 
                _class.getElementsByTagName('line'))
    run = sum([1 for line in lines if int(line['h']) > 0])
    missing = sum([1 for line in lines if int(line['h']) == 0])
    excluded = 0 # not sure how to get this value
    partial = sum([1 for line in lines if line['c']])
    branches = sum([int(line['c'].split('/')[-1][:-1]) for line in lines if line['c']])

    return _class.getAttribute('filename'), {
        "br": _class.getAttribute('branch-rate'),
        "c": _class.getAttribute('complexity'),
        "f": _class.getAttribute('filename'),
        "b": branches,
        "r": run,
        "m": missing,
        "e": excluded,
        "p": partial,
        "s": sum([run, missing, partial]),
        "cov": ("%d" % int(round(float(run)/float(run+missing+partial)*100))) if run else "0",
        "lr": _class.getAttribute('line-rate'),
        # "name": _class.getAttribute('name'),
        "lines": lines}


def main():
    defaults = dict()

    if os.getenv('CI') == "true" and os.getenv('TRAVIS') == "true":
        # http://docs.travis-ci.com/user/ci-environment/#Environment-variables
        defaults = dict(repo=os.getenv('TRAVIS_REPO_SLUG'),
                        branch=os.getenv('TRAVIS_BRANCH'),
                        travis_job_id=os.getenv('TRAVIS_JOB_ID'),
                        xml=os.path.join(os.getenv('TRAVIS_BUILD_DIR'), "coverage.xml"),
                        commit=os.getenv('TRAVIS_COMMIT'))

    elif os.getenv('CI_NAME') == 'codeship':
        # https://www.codeship.io/documentation/continuous-integration/set-environment-variables/
        defaults = dict(branch=os.getenv('CI_BRANCH'),
                        commit=os.getenv('CI_COMMIT_ID'))

    elif os.getenv('CIRCLECI') == 'true':
        # https://circleci.com/docs/environment-variables
        defaults = dict(branch=os.getenv('CIRCLE_BRANCH'),
                        repo=[os.getenv('CIRCLE_PROJECT_USERNAME'), os.getenv('CIRCLE_PROJECT_REPONAME')],
                        commit=os.getenv('CIRCLE_SHA1'))

    else:
        # find branch, commit, repo from git command
        defaults.update(branch=commands.getstatusoutput('git branch')[1].replace('* ', ''),
                        commit=commands.getstatusoutput('git rev-parse HEAD')[1],
                        repo=re.search(r"\w+(\s+|\t)(\w+)://github.com/([^\.]+).git\s", commands.getstatusoutput('git remote -v | grep github.com | head -1')[1]).groups()[2])

    parser = argparse.ArgumentParser(prog='codecov', add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Example: \033[90mcodecov stevepeak timestring 817vnp1\033[0m\nRead more at \033[95mhttps://codecov.io/\033[0m""")
    parser.add_argument('--version', action='version', version='codecov '+version+" - https://codecov.io")
    parser.add_argument('repo', nargs="?", help="repo name")
    parser.add_argument('--commit', default=defaults.get('commit'), help="commit ref")
    parser.add_argument('--branch', default=defaults.get('branch', 'master'), help="commit branch name")
    parser.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), help="codecov repository token")
    parser.add_argument('--xml', '-x', default="coverage.xml", help="coverage xml report relative path")
    parser.add_argument('--url', default="https://codecov.io", help="url, used for debugging")
    codecov = parser.parse_args()

    if not codecov.repo:
        codecov.repo = defaults['repo']

    if type(codecov.repo) in (tuple, list):
        codecov.repo = "/".join(codecov.repo)

    assert codecov.repo is not None, "codecov: repo (owner/name) is required"
    assert codecov.branch is not None, "codecov: branch is required"
    assert codecov.commit is not None, "codecov: commit hash is required"
    if os.getenv('TRAVIS') != "true":
        assert codecov.token is not None, "codecov: token is required if not using travis-ci, codeship or circleci"

    try:
        coverage = generate_report(codecov.xml)
        if not coverage:
            sys.stdout.write("codecov: Error no coverage.xml report found, could not upload to codecov\n")
    except:
        sys.stdout.write("codecov: Error failed to process report for codecov\n")
        raise

    else:
        url = "%s/%s?commit=%s&version=%s&token=%s&branch=%s&travis_job_id=%s" % (codecov.url, codecov.repo, codecov.commit, version, (codecov.token or ''), codecov.branch, defaults.get('travis_job_id', ''))
        result = requests.post(url, headers={"Accept": "application/json"}, data=dumps(coverage))
        sys.stdout.write(result.text+"\n")


if __name__ == '__main__':
    main()
