#   pybuilder_header_plugin
#   Copyright 2014 Michael Gruber
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from fnmatch import filter
from os import walk
from os.path import join

from pybuilder.errors import PyBuilderException
from pybuilder.core import task, description, depends


def check_file(file_name, expected_header, logger):

    with open(file_name, 'r') as source_file:
        line_number = 0
        for line in expected_header.split('\n'):
            line_number += 1
            source_line = source_file.readline()[:-1]
            if line != source_line:
                prefix = file_name + ":" + str(line_number) + " "
                message = 'Expected header in line {} is: '.format(line_number).rjust(len(prefix))
                logger.warn(prefix + source_line)
                logger.warn(message + line)
                return True
    return False


def find_matching_files(source_directory):
    matching_files = []
    for root, directory_names, file_names in walk(source_directory):
        for filename in filter(file_names, '*.py'):
            path = join(root, filename)
            matching_files.append(path)

    return matching_files


def search_in_directory(source_directory, expected_header, logger):
    affected_files = 0

    matching_files = find_matching_files(source_directory)

    for file_name in matching_files:
        found_something = check_file(file_name, expected_header, logger)

        if found_something:
            affected_files += 1

    return affected_files


@task('check_source_file_headers')
@description('Ensures that the source files have the expected header')
@depends('analyze')
def check_source_file_headers(project, logger):

    expected_header = project.get_property('pybuilder_header_plugin_expected_header')
    break_build = project.get_property('pybuilder_header_plugin_break_build')

    if break_build and not expected_header:
        raise PyBuilderException('Please specify expected file header!')

    affected_files = 0

    source_directory = join('src', 'main', 'python')
    affected_files += search_in_directory(source_directory, expected_header, logger)

    test_directory = join('src', 'unittest', 'python')
    affected_files += search_in_directory(test_directory, expected_header, logger)

    if affected_files > 0:
        message = "Found %d source files containing unexpected header." % affected_files

        if break_build:
            raise PyBuilderException(message)
        else:
            logger.warn(message)
