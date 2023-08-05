#   shtub - shell command stub
#   Copyright (C) 2012-2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
    shtub - shell command stub.
"""

__author__ = 'Alexander Metzner, Michael Gruber, Udo Juettner'

import json
import logging
import fcntl

import os
from os.path import join

from shtub.execution import Execution
from shtub.stubconfiguration import StubConfiguration

__version__ = '0.3.8'

BASEDIR = 'shtub'

EXECUTIONS_FILENAME = join(BASEDIR, 'executions')
CONFIGURED_STUBS_FILENAME = join(BASEDIR, 'stub-configurations')
LOCK_FILENAME = join(BASEDIR, 'lock')
SERIALIZATION_LOCK_FILENAME = join(BASEDIR, 'serialization-lock')
LOG_FILENAME = join(BASEDIR, 'log')
STUBS_DIRECTORY = join(BASEDIR, 'stubs')

READ_STDIN_TIMEOUT_IN_SECONDS = 1


def deserialize_stub_configurations (filename):
    """
        loads the given json file and returns a list of stub configurations.
    """
    stub_configurations = _load_json_file(filename)
    return list(map(lambda e: StubConfiguration.from_dictionary(e), stub_configurations))


def deserialize_executions (filename):
    """
        loads the given json file and returns a list of executions.
    """
    executions = _load_json_file(filename)
    return list(map(lambda e: Execution.from_dictionary(e), executions))


def serialize_as_dictionaries (filename, dictionarizables):
    """
        writes the given execution objects into a json file with the given filename.
    """
    dictionaries = list(map(lambda e: e.as_dictionary(), dictionarizables))
    json_string = json.dumps(dictionaries, sort_keys=True, indent=4)

    with open(filename, mode='w') as json_file:
        json_file.write(json_string)

def _load_json_file (filename):
    """
        loads the given json file and returns the json content as dictionary.
    """
    with open(filename, mode='r') as json_file:
        file_content = json_file.read()
        dictionary = json.loads(file_content)

    return dictionary


def lock (file_name=LOCK_FILENAME):
    """
        creates a file lock and blocks if the file lock is already taken.
    """
    if not os.path.exists(BASEDIR):
        os.mkdir(BASEDIR)

    logging.info('Acquire lock.')
    file_handle = open(file_name, mode='a')
    fcntl.flock(file_handle, fcntl.LOCK_EX)

    logging.info('Lock acquired.')
    return file_handle


def unlock (file_handle):
    """
        releases the given file lock by closing it.
    """

    logging.info('Lock released.')
    file_handle.close()
