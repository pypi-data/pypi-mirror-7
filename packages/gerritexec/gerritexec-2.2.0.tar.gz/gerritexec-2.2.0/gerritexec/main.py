#
# Copyright (C) 2013,2014 <libre.licensing@cloudwatt.com>
#
# Author: Loic Dachary <loic@dachary.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see `<http://www.gnu.org/licenses/>`.
#
import argparse
import logging
import os
import re
import shutil
import subprocess

from gerritlib import gerrit


class GerritExec(gerrit.Gerrit):

    def __init__(self, options):
        super(GerritExec, self).__init__(options.hostname, options.username,
                                         port=options.port,
                                         keyfile=options.keyfile)
        self.directory = options.directory
        self.script = options.script
        self.project = options.project
        self.timeout = options.timeout
        self.banner = ("Gerritexec oneliner verification starts "
                       "https://pypi.python.org/pypi/gerritexec ")

    def loop(self):
        self.startWatching()
        while True:
            event = self.getEvent()
            if not event:
                break
            logging.debug("Event: %s", event)
            if ((event['type'] == 'patchset-created' and
                 event['change']['project'] == self.project)):
                self.patchset_created(event)
            elif ((event['type'] == 'comment-added' and
                   event['change']['project'] == self.project)):
                self.comment_added(event)

    def git_url(self, event):
        return 'https://' + self.hostname + '/' + event['change']['project']

    def comment_added(self, event):
        if ((re.match(r".*recheck\s+no\s+bug\s*",
                      event['comment'], re.DOTALL) or
             re.match(r".*run\s+gerritexec\s*",
                      event['comment'], re.DOTALL))):
            self.pre_verify(event)
            self.verify(event)

    def patchset_created(self, event):
        self.pre_verify(event)
        self.verify(event)

    def pre_verify(self, event):
        self.review(event['change']['project'],
                    event['patchSet']['revision'],
                    self.banner,
                    {'verified': '0'})

    def verify(self, event):
        directory = self.directory
        shutil.rmtree(directory, ignore_errors=True)
        output = ""
        try:
            cmd = 'git clone ' + self.git_url(event) + ' ' + directory
            output += cmd + "\n"
            output += subprocess.check_output(cmd,
                                              stderr=subprocess.STDOUT,
                                              shell=True)
            cmd = ("cd '" + directory + "' && " + "git pull " +
                   self.git_url(event) +
                   " " + event['patchSet']['ref'])
            output += cmd + "\n"
            output += subprocess.check_output(cmd,
                                              stderr=subprocess.STDOUT,
                                              shell=True)
            cmd = ("cd " + directory + " && " +
                   " timeout %d " % self.timeout +
                   self.script + ' "%s"' % str(event))
            logging.debug(cmd)
            output += "timeout %d %s\n" % (self.timeout, self.script)
            output += subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                              shell=True)
            verified = '+1'
        except subprocess.CalledProcessError as e:
            output += e.output
            verified = '-1'
        self.review(event['change']['project'],
                    event['patchSet']['revision'],
                    output,
                    {'verified': verified})


def main(argv):
    parser = argparse.ArgumentParser(
        description="Run a command when a patchset is created")

    parser.add_argument('--hostname', dest='hostname',
                        help='gerrit hostname', required=True)
    parser.add_argument('--username', dest='username',
                        help='username', required=True)
    parser.add_argument('--port', dest='port', type=int,
                        help='gerrit port number',
                        default=29418)
    parser.add_argument('--timeout', dest='timeout', type=int,
                        help='script timeout in seconds',
                        default=3600)
    parser.add_argument('--identity', dest='keyfile',
                        help='ssh identity file',
                        default=os.path.expanduser('~/.ssh/id_rsa'))
    parser.add_argument('--directory', dest='directory',
                        help='destination directory for clone',
                        default='downstream')
    parser.add_argument('--script', dest='script',
                        help='script to run',
                        required=True)
    parser.add_argument('--project', dest='project',
                        help='only act on project patchset',
                        required=True)
    parser.add_argument('--verbose', dest='verbose',
                        action='store_const',
                        const=True,
                        help='enable verbose (debug) logging')

    args = parser.parse_args(argv)

    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=level)

    GerritExec(args).loop()
