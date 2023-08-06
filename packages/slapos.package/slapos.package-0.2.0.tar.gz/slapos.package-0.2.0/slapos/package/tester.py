#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set et sts=2:
##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors.
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

import ConfigParser
import logging
from optparse import OptionParser, Option
import os
import sys
import tempfile
import urllib2


# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)



class Parser(OptionParser):
  """
  Parse all arguments.
  """
  def __init__(self, usage=None, version=None):
    """
    Initialize all options possibles.
    """
    OptionParser.__init__(self, usage=usage, version=version,
                          option_list=[
      Option("--slapos-configuration",
             help="path to slapos configuration directory",
             default='/etc/opt/slapos/',
             type=str),
      Option("--slapos-cron",
             help="path to slapos cron file",
             default='/etc/cron.d/slapos-node',
             type=str),
      Option("--check-upload",
             help="Check if upload parameters are ok (do not check certificates)",
             default=False,
             action="store_true"),
      Option("--test-agent",
             help="Check if parameters are good for a test agent",
             default=False,
             action="store_true"),
      Option("-v","--verbose",
             default=False,
             action="store_true",
             help="Verbose output."),
      Option("-n", "--dry-run",
             help="Simulate the execution steps",
             default=False,
             action="store_true"),
   ])

  def check_args(self):
    """
    Check arguments
    """
    (options, args) = self.parse_args()
    if options.test_agent:
      options.check_upload = True
    return options


def get_slapos_conf_example():
  """
  Get slapos.cfg.example and return its path
  """
  register_server_url = "http://git.erp5.org/gitweb/slapos.core.git/blob_plain/HEAD:/slapos.cfg.example"
  request = urllib2.Request(register_server_url)
  url = urllib2.urlopen(request)
  page = url.read()
  info, path = tempfile.mkstemp()
  slapos_cfg_example = open(path,'w')
  slapos_cfg_example.write(page)
  slapos_cfg_example.close()
  return path


def check_networkcache(config, logger, configuration_parser,
                       configuration_example_parser):
  """
  Check network cache download
  """
  section = "networkcache"
  if configuration_parser.has_section(section):
    configuration_example_dict = dict(configuration_example_parser.items(section))
    configuration_dict = dict(configuration_parser.items(section))
    for key in configuration_example_dict:
      try:
        if not configuration_dict[key] ==  configuration_example_dict[key]:
          logger.warn("%s parameter in %s section is out of date" % (key, section))
      except KeyError:
        logger.warn("No %s parameter in %s section" % (key, section))
        pass

    if config.test_agent:
      configuration_dict = dict(configuration_parser.items('slapformat'))
      if int(configuration_dict['partition_amount']) < 60:
        logger.warn("Partition amount is to low for a test agent. Is %s but should be at least 60"
                    % configuration_dict['partition_amount'] )

    if config.check_upload == True:
      check_networkcache_upload(config, logger, configuration_dict)


class Upload:
  """
  Class used as a reference to check network cache upload
  """
  def __init__(self):
    self.data = {'download-binary-dir-url': 'http://www.shacache.org/shadir',
                 'signature_certificate_file': '/etc/slapos-cache/signature.cert',
                 'upload-dir-url': 'https://www.shacache.org/shadir',
                 'shadir-cert-file': '/etc/slapos-cache/shacache.cert',
                 'download-cache-url': 'https://www.shacache.org/shacache',
                 'upload-cache-url': 'https://www.shacache.org/shacache',
                 'shacache-cert-file': '/etc/slapos-cache/shacache.cert',
                 'upload-binary-cache-url': 'https://www.shacache.org/shacache',
                 'shacache-key-file': '/etc/slapos-cache/shacache.key',
                 'download-binary-cache-url': 'http://www.shacache.org/shacache',
                 'upload-binary-dir-url':'https://www.shacache.org/shadir',
                 'signature_private_key_file': '/etc/slapos-cache/signature.key',
                 'shadir-key-file': '/etc/slapos-cache/shacache.key'}


def check_networkcache_upload(config, logger, configuration_dict):
  """
  Check network cache upload
  """
  upload_parameters = Upload()
  for key in upload_parameters.data:
    try:
      if not key.find("file") == -1:
        file = configuration_dict[key]
        if not os.path.exists(file):
          logger.critical ("%s file for %s parameters does not exist "
                         % (file, key))
        else:
          logger.info ("%s parameter:%s does exists" % (key, file))
      else:
        if not configuration_dict[key] == upload_parameters.data[key]:
          logger.warn("%s is %s sould be %s"
                      % (
                          key,
                          configuration_dict[key],
                          upload_parameters.data[key]
                          )
                      )
    except KeyError:
      logger.critical("No %s parameter in networkcache section "
                        % (key))
      pass

def get_computer_name(certificate):
  """
  Extract computer_id for certificate
  """
  certificate = open(certificate,"r")
  for line in certificate:
    i = 0
    if "Subject" in line:
      k=line.find("COMP-")
      i=line.find("/email")
      certificate.close()
      return line[k:i]
  return -1

def check_computer_id(logger,computer_id,cert_file):
  """
  Get computer id from cert_file and compare with computer_id
  """
  comp_cert = get_computer_name(cert_file)
  if comp_cert == "":
    logger.error("Certificate file indicated is corrupted (no computer id)")
  elif comp_cert == computer_id:
      logger.info("Certificate and slapos.cfg define same computer id: %s"
                   % computer_id)
  else:
    logger.critical("Computers id from cerificate (%s) is different from slapos.cfg (%s)"
                    % (comp_cert,computer_id))

def slapos_conf_check (config):
  """
  Check if slapos.cfg look good
  """
  # Define logger for slapos.cfg verification
  logger = logging.getLogger('Checking slapos.cfg file:')
  logger.setLevel(logging.INFO)
  logger.addHandler(ch)
  # Load configuration file
  configuration_file_path = os.path.join (config.slapos_configuration
                                          ,'slapos.cfg')
  configuration_parser = ConfigParser.SafeConfigParser()
  configuration_parser.read(configuration_file_path)
  # Get example configuration file
  slapos_cfg_example = get_slapos_conf_example()
  configuration_example_parser = ConfigParser.RawConfigParser()
  configuration_example_parser.read(slapos_cfg_example)
  os.remove(slapos_cfg_example)

  # Check sections
  mandatory_sections = ["slapos","slapformat","networkcache"]
  for section in mandatory_sections:
    if not configuration_parser.has_section(section):
      logger.critical("No %s section in slapos.cfg" % section)
      mandatory_sections.remove(section)

  if 'networkcache' in mandatory_sections:
    mandatory_sections.remove('networkcache')

  # Check if parameters for slapos and slapformat exists
  for section in mandatory_sections:
    configuration_dict = dict(configuration_parser.items(section))
    configuration_example_dict = dict(configuration_example_parser.items(section))
    for key in configuration_example_dict:
      if not key in configuration_dict:
        logger.critical("No %s parameter in %s section "
                        % (key,section))
      # check if necessary files exist
      elif key in ("key_file","cert_file","certificate_repository_path"):
        files = configuration_dict[key]
        if not os.path.exists(files):
          logger.critical ("%s file for %s parameters does not exist "
                           % (files,key))
        else:
          logger.info ("%s parameter:%s does exists" % (key,files))
      # check if computer id is the same in slapos.cfg and certificate
      if key == "cert_file":
        check_computer_id(logger,configuration_dict["computer_id"],
                          configuration_dict["cert_file"])
  # Check networkcache
  check_networkcache(config,logger,configuration_parser,
                     configuration_example_parser)


class CronFile:
  """
  Class to analyse each cron line individualy
  """
  def __init__(self):
    """ Init all values"""
    self.slapformat  = -1
    self.slapgrid_cp = -1
    self.slapgrid_ur = -1
    self.slapgrid_sr = -1
    # cron file from slapos documentation
    self.slapgrid_sr_base = "* * * * * root /opt/slapos/bin/slapos node software --verbose --logfile=/opt/slapos/log/slapos-node-software.log > /dev/null 2>&1"
    self.slapgrid_cp_base = "* * * * * root /opt/slapos/bin/slapos node instance --verbose --logfile=/opt/slapos/log/slapos-node-instance.log > /dev/null 2>&1"
    self.slapgrid_ur_base = "0 * * * * root /opt/slapos/bin/slapos node report --maximal_delay=3600 --verbose --logfile=/opt/slapos/log/slapos-node-report.log > /dev/null 2>&1"
    self.slapformat_base = "0 * * * * root /opt/slapos/bin/slapos node format >> /opt/slapos/log/slapos-node-format.log 2>&1"


  def parse(self,cron_line):
    """ Parse cron line and give value to attributes """
    line = cron_line.split()
    if "slapos node format"  in cron_line:
      self.slapformat  = self.compare(self.slapformat,
                                      self.slapformat_base.split()  , line)
    if "slapos node report" in cron_line:
      self.slapgrid_ur = self.compare(self.slapgrid_ur,
                                      self.slapgrid_ur_base.split() , line)
    if "slapos node instance" in cron_line:
      self.slapgrid_cp = self.compare(self.slapgrid_cp,
                                      self.slapgrid_cp_base.split() , line)
    if "slapos node software" in cron_line:
      self.slapgrid_sr = self.compare(self.slapgrid_sr,
                                      self.slapgrid_sr_base.split() , line)

  def compare(self, state, reference, cron_line):
    if not state == -1:
      return 2
    for i in range(0, 6):
      if not reference[i] == cron_line[i]:
        return 0
    ref = len(set(reference[6:]))
    if not len(set(reference[6:]) & set(cron_line[6:])) == ref:
      return 0
    else: return 1

  def check(self, logger):
    elements = {
            'slapos node format': self.slapformat,
            'slapos node report': self.slapgrid_ur,
            'slapos node software': self.slapgrid_sr,
            'slapos node instance': self.slapgrid_cp
            }
    for key in elements:
      if elements[key] == 0:
        logger.error("Your line for '%s' command does not seem right" % key)
      elif elements[key] == -1:
        logger.error("No line found for '%s' command" % key)
      elif elements[key] == 1:
        logger.info("Line for '%s' command is good" % key)
      elif elements[key] == 2:
        logger.error("You have a duplicated line for '%s' command" % key)



def cron_check (config):
  """
  Check cron file
  """
  # Define logger for cron file verification
  logger = logging.getLogger('Checking slapos-node cron file:')
  logger.setLevel(logging.INFO)
  logger.addHandler(ch)
  cron = open(config.slapos_cron,"r")
  cron_file = CronFile()
  for line in cron:
    if "/opt/slapos" in line and not line[0]=="#":
      cron_file.parse(line)
  cron_file.check(logger)

def slapos_global_check (config):
  """
  Check for main files
  """
  # Define logger for computer chek
  logger = logging.getLogger('Checking your computer for SlapOS:')
  logger.setLevel(logging.INFO)
  logger.addHandler(ch)
  # checking slapos.cfg
  if not os.path.exists(os.path.join(config.slapos_configuration,'slapos.cfg')):
    logger.critical("No slapos.cfg found in slapos configuration directory: %s"
                    % config.slapos_configuration )
  else:
    logger.info("SlapOS configuration file found")
    slapos_conf_check(config)
  # checking cron file
  if not os.path.exists(config.slapos_cron):
    logger.warn("No %s found for cron" % config.slapos_cron)
  else:
    logger.info("Cron file found at %s" %config.slapos_cron)
    cron_check(config)

# Class containing all parameters needed for configuration
class Config:
  def setConfig(self, option_dict):
    """
    Set options given by parameters.
    """
    # Set options parameters
    for option, value in option_dict.__dict__.items():
      setattr(self, option, value)
    # Define logger for register
    self.logger = logging.getLogger('slapos-test configuration')
    self.logger.setLevel(logging.DEBUG)
    # add ch to logger
    self.logger.addHandler(ch)

    if self.verbose:
      ch.setLevel(logging.DEBUG)


  def displayUserConfig(self):
    self.logger.debug ("Slapos.cfg : %s" % self.slapos_configuration)
    self.logger.debug ("slapos cron file: %s" % self.slapos_cron)


def main():
  """Checking computer state to run slapos"""
  usage = "usage: %s [options] " % sys.argv[0]
  # Parse arguments
  config = Config()
  config.setConfig(Parser(usage=usage).check_args())
  config.displayUserConfig()
  slapos_global_check(config)
  sys.exit()


if __name__ == "__main__":
  main()
