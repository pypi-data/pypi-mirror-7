#!/usr/bin/env python
# vim: set fileencoding=utf-8
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import subprocess
import os
import sys
import argparse

import facereclib

def command_line_arguments(command_line_parameters):
  """Defines the command line parameters that are accepted."""

  # create parser
  parser = argparse.ArgumentParser(description='Execute baseline algorithms with default parameters', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # add parameters
  # - the database to choose
  parser.add_argument('-d', '--database', default = 'atnt', help = 'The database on which the baseline algorithm is executed.')
  # - the features directory
  parser.add_argument('--features-directory', metavar = 'DIR', required=True, help = 'The directory containing the feature files.')
  # - the protocol if required
  parser.add_argument('-P', '--protocol', metavar='PROTOCOL', help = 'Overwrite the protocol that is stored in the database by the given one (might not by applicable for all databases).')

  # - the tool configuration
  parser.add_argument('-t', '--tool', default = 'mygmm', help = 'Recognition tool (algorithm) configuration.')
  # - the grid configuration -- option is only useful if you are at Idiap
  parser.add_argument('-g', '--grid', default = None, help = 'Configuration file for the grid setup; if not specified, the commands are executed sequentially on the local machine.')

  # - the subdirectory for this specific experiment
  parser.add_argument('-b', '--sub-directory', metavar = 'DIR', default = 'gmm', help = 'The sub-directory where the files of the current experiment should be stored. Please specify a directory name with a name describing your experiment.')
  # - the temp directory
  parser.add_argument('-T', '--temp-directory', metavar = 'DIR', help = 'The directory for temporary files; if not specified, "temp" in the current directory is used.')
  # - the user directory
  parser.add_argument('-U', '--result-directory', '--user-directory', dest='user_directory', metavar = 'DIR', help = 'The directory for resulting score files; if not specified, "results" in the current directory is used.')

  # - just print?
  parser.add_argument('-q', '--dry-run', action = 'store_true', help = 'Just print the commands, but do not execute them.')

  # - other parameters that are passed to the underlying script
  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = 'Parameters directly passed to the face verification script.')

  facereclib.utils.add_logger_command_line_option(parser)
  args = parser.parse_args(command_line_parameters)
  facereclib.utils.set_verbosity_level(args.verbose)

  return args


# Some default variables that are required
thesis_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
bin_dir = os.path.join(thesis_dir, 'bin')
config_dir = os.path.join(thesis_dir, 'xbob/gender/bimodal/configurations')
script = os.path.join(bin_dir, 'faceverify.py')


def main(command_line_parameters = sys.argv):

  # Collect command line arguments
  args = command_line_arguments(command_line_parameters[1:])

  facereclib.utils.info("Executing algorithm 'GMM'")

  # create the command to the faceverify script
  command = [
              script,
              '--database', args.database,
              '--preprocessing', 'face-crop',
              '--features', 'dct',
              '--tool', args.tool,
              '--sub-directory', args.sub_directory,
              '--features-directory', args.features_directory,
            ]

  # protocol, if provided
  if args.protocol:
    command.extend(['--protocol', args.protocol])

  # user directory
  if args.user_directory:
    command.extend(['--user-directory', args.user_directory])

  # temp directory
  if args.temp_directory:
    command.extend(['--temp-directory', args.temp_directory])

  # add grid argument, if available
  if args.grid:
    command.extend(['--grid', args.grid])

  # set the verbosity level
  if args.verbose:
    command.append('-' + 'v'*args.verbose)

  # Add skips
  command.extend(['--skip-preprocessing', '--skip-extractor-training', '--skip-extraction', '--skip-enroller-training', '--skip-enrollment', '--skip-score-computation', '--skip-concatenation'])

  # add the command line arguments that were specified on command line
  if args.parameters:
    command.extend(args.parameters[1:])

  # print the command so that it can easily be re-issued
  facereclib.utils.info("Executing command:")
  print(" ".join(command))

  # run the command
  if not args.dry_run:
    subprocess.call(command)


if __name__ == "__main__":
  main()

