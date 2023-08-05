# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2011, 2012 Vifib SARL and Contributors.
# All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import argparse
import ConfigParser
import logging
import sys
import os

from slapos.format import FormatConfig, UsageError, tracing_monkeypatch, do_format


def main(*args):
  "Run default configuration."

  ap = argparse.ArgumentParser()

  ap.add_argument('-x', '--computer_xml',
                  help="Path to file with computer's XML. If does not exists, will be created",
                  default=None)

  ap.add_argument('--computer_json',
                  help="Path to a JSON version of the computer's XML (for development only).",
                  default=None)

  ap.add_argument('-l', '--log_file',
                  help="The path to the log file used by the script.")

  ap.add_argument('-i', '--input_definition_file',
                  help="Path to file to read definition of computer instead of "
                  "declaration. Using definition file allows to disable "
                  "'discovery' of machine services and allows to define computer "
                  "configuration in fully controlled manner.")

  ap.add_argument('-o', '--output_definition_file',
                  help="Path to file to write definition of computer from "
                  "declaration.")

  ap.add_argument('-n', '--dry_run',
                  help="Don't actually do anything.",
                  default=False,
                  action="store_true")

  ap.add_argument('-v', '--verbose',
                  default=False,
                  action="store_true",
                  help="Verbose output.")

  # the console option is actually ignored and not used anymore.
  ap.add_argument('-c', '--console',
                  default=False,
                  action="store_true",
                  help="Console output.")

  ap.add_argument('--alter_user',
                  choices=['True', 'False'],
                  help="Shall slapformat alter user database [default: True]")

  ap.add_argument('--alter_network',
                  choices=['True', 'False'],
                  help="Shall slapformat alter network configuration [default: True]")

  ap.add_argument('--now',
                  help="Launch slapformat without delay",
                  default=False,
                  action="store_true")

  ap.add_argument('configuration_file',
                  help='path to slapos.cfg')

  if args:
    args = ap.parse_args(list(args))
  else:
    args = ap.parse_args()

  logger = logging.getLogger("slapformat")
  logger.addHandler(logging.StreamHandler())

  if args.verbose:
    logger.setLevel(logging.DEBUG)
    logger.debug("Verbose mode enabled.")
  else:
    logger.setLevel(logging.INFO)

  conf = FormatConfig(logger=logger)

  configp = ConfigParser.SafeConfigParser()
  if configp.read(args.configuration_file) != [args.configuration_file]:
    raise UsageError('Cannot find or parse configuration file: %s' % args.configuration_file)

  conf.mergeConfig(args, configp)

  if conf.log_file:
    if not os.path.isdir(os.path.dirname(conf.log_file)):
      # fallback to console only if directory for logs does not exists and
      # continue to run
      raise ValueError('Please create directory %r to store %r log file' % (
        os.path.dirname(conf.log_file), conf.log_file))
    else:
      file_handler = logging.FileHandler(conf.log_file)
      file_handler.setFormatter(logging.Formatter("%(asctime)s - "
        "%(name)s - %(levelname)s - %(message)s"))
      conf.logger.addHandler(file_handler)
      conf.logger.info('Configured logging to file %r' % conf.log_file)

  try:
    conf.setConfig()
  except UsageError as exc:
    sys.stderr.write(exc.message + '\n')
    sys.stderr.write("For help use --help\n")
    sys.exit(1)

  tracing_monkeypatch(conf)

  try:
    do_format(conf=conf)
  except:
    conf.logger.exception('Uncaught exception:')
    raise
