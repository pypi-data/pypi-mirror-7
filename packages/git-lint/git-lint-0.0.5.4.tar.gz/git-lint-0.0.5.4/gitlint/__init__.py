# Copyright 2013-2014 Sebastian Kreft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
git-lint: improving source code one step at a time

Lints all the modified files in your git repository showing only the modified
lines.

It supports many filetypes, including:
    PHP, Python, Javascript, Ruby, CSS, SCSS, PNG, JPEG, RST, YAML, INI, Java,
    among others. See https://github.com/sk-/git-lint for the complete list.

Usage:
    git-lint [-f | --force] [FILENAME ...]
    git-lint [-t | --tracked] [-f | --force]
    git-lint -h | --version

Options:
    -h            Show the usage patterns.
    --version     Prints the version number.
    -f --force    Shows all the lines with problems.
    -t --tracked  Lints only tracked files.
"""

import os.path
import sys

import docopt
import termcolor
import yaml

import gitlint.git as git
import gitlint.linters as linters


__VERSION__ = '0.0.2'


def find_invalid_filenames(filenames, repository_root):
    """Find files that does not exist, are not in the repo or are directories.

    Args:
      filenames: list of filenames to check
      repository_root: the absolute path of the repository's root.

    Returns: A list of errors.
    """
    errors = []
    for filename in filenames:
        if not os.path.abspath(filename).startswith(repository_root):
            errors.append((filename, 'Error: File %s does not belong to '
                          'repository %s' % (filename, repository_root)))
        if not os.path.exists(filename):
            errors.append((filename,
                          'Error: File %s does not exist' % (filename, )))
        if os.path.isdir(filename):
            errors.append((filename, 'Error: %s is a directory. Directories are'
                          ' not yet supported' % (filename, )))

    return errors


def get_config():
    """Gets the configuration file either from the repository or the default."""
    config = os.path.join(os.path.dirname(__file__), 'configs', 'config.yaml')
    repo_root = git.repository_root()

    if repo_root:
        repo_config = os.path.join(repo_root, '.gitlint.yaml')
        if os.path.exists(repo_config):
            config = repo_config

    with open(config) as f:
        # We have to read the content first as yaml hangs up when reading from
        # MockOpen
        content = f.read()
        # Yaml.load will return None when the input is empty.
        if not content:
            yaml_config = {}
        else:
            yaml_config = yaml.load(content)

    return linters.parse_yaml_config(yaml_config, repo_root)


def main(argv):
    """Main gitlint routine. To be called from scripts."""
    arguments = docopt.docopt(__doc__,
                              argv=argv[1:],
                              version='git-lint v%s' % __VERSION__)

    repository_root = git.repository_root()
    if repository_root is None:
        sys.stderr.write('fatal: Not a git repository' + os.linesep)
        return 128

    if arguments['FILENAME']:
        invalid_filenames = find_invalid_filenames(arguments['FILENAME'],
                                                   repository_root)
        if invalid_filenames:
            invalid_filenames.append(('', ''))
            sys.stderr.write(
                os.linesep.join(invalid[1] for invalid in invalid_filenames))
            return 2

        changed_files = git.modified_files(repository_root,
                                           tracked_only=arguments['--tracked'])
        modified_files = {}
        for filename in arguments['FILENAME']:
            normalized_filename = os.path.abspath(filename)
            modified_files[normalized_filename] = changed_files.get(
                normalized_filename)
    else:
        modified_files = git.modified_files(repository_root,
                                            tracked_only=arguments['--tracked'])

    linter_not_found = False
    files_with_problems = 0
    gitlint_config = get_config()

    for filename in sorted(modified_files.keys()):
        rel_filename = os.path.relpath(filename)
        print('Linting file: %s' % termcolor.colored(rel_filename,
                                                     attrs=('bold',)))
        if arguments['--force']:
            modified_lines = None
        else:
            modified_lines = git.modified_lines(filename,
                                                modified_files[filename])

        result = linters.lint(
            filename, modified_lines, gitlint_config)

        if result == 'OK':
            result = termcolor.colored(result, 'green', attrs=('bold',))
        elif result.startswith('SKIPPED:'):
            result = result.replace(
                'SKIPPED',
                termcolor.colored('SKIPPED', 'yellow', attrs=('bold',)))
        elif result.startswith('ERROR:'):
            result = result.replace(
                'ERROR',
                termcolor.colored('ERROR', 'red', attrs=('bold',)))
            linter_not_found = True
        else:
            files_with_problems += 1

        print(result)
        print('')

    if files_with_problems > 0:
        return 1
    if linter_not_found:
        return 4
    return 0
