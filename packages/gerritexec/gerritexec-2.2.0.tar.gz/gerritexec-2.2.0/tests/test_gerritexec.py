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
import fixtures
import mock
import os
import Queue
import testtools

from gerritexec import main


class GitFixture(fixtures.TempDir):

    def setUp(self):
        super(GitFixture, self).setUp()
        self.url = os.path.join(self.path, "upstream")
        self.ref = "THEREF"
        self.file_only_in_ref = "ONLY_IN_REF"
        self.script = "./gerrittestscript"
        os.system("""
cd {path}
mkdir upstream
cd upstream
git init
echo abc > a
git add a
git commit -m 'a' a
git branch {ref}
git checkout {ref}
echo def > {file}
cat > {script} <<'EOF'
#!/bin/bash
echo -n "$@"
EOF
chmod +x {script}
git add {file} {script}
git commit -m 'ONLY HERE'
git checkout master
""".format(path=self.path,
           ref=self.ref,
           file=self.file_only_in_ref,
           script=self.script))


class TestGerritExec(testtools.TestCase):

    @mock.patch('gerritexec.main.GerritExec')
    def test_main(self, mock_GerritExec):
        self.assertRaises(SystemExit, main.main,
                          ['--username', 'USERNAME'])
        self.assertRaises(SystemExit, main.main,
                          ['--hostname', 'HOST'])

        main.main(['--hostname', 'HOST',
                   '--username', 'USERNAME',
                   '--script', 'SCRIPT',
                   '--project', 'PROJECT',
                   '--identity', 'id_rsa'])
        args = argparse.Namespace(hostname='HOST',
                                  keyfile='id_rsa',
                                  port=29418,
                                  timeout=3600,
                                  username='USERNAME',
                                  directory='downstream',
                                  script='SCRIPT',
                                  project='PROJECT',
                                  verbose=None)
        mock_GerritExec.assert_called_with(args)

        main.main(['--hostname', 'HOST',
                   '--username', 'USERNAME',
                   '--identity', 'id_rsa',
                   '--timeout', '1200',
                   '--directory', 'DOWNSTREAM',
                   '--script', 'SCRIPT',
                   '--project', 'PROJECT',
                   '--verbose'])
        args = argparse.Namespace(hostname='HOST',
                                  keyfile='id_rsa',
                                  port=29418,
                                  timeout=1200,
                                  username='USERNAME',
                                  directory='DOWNSTREAM',
                                  script='SCRIPT',
                                  project='PROJECT',
                                  verbose=True)
        mock_GerritExec.assert_called_with(args)

    @mock.patch.object(main.GerritExec, 'git_url')
    @mock.patch.object(main.GerritExec, 'startWatching')
    @mock.patch.object(main.GerritExec, 'review')
    def test_loop(self, mock_review, mock_startWatching, mock_git_url):
        fixture = self.useFixture(GitFixture())
        downstream = os.path.join(fixture.path, "downstream")
        script = fixture.script
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=1200,
                                                    username='USERNAME',
                                                    directory=downstream,
                                                    script=script,
                                                    project='project-name',
                                                    verbose=True))
        revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadb"
        mock_git_url.side_effect = lambda event: fixture.url
        gerrit.event_queue = Queue.Queue()
        patchset_created = {"type": "patchset-created",
                            "change": {"project": gerrit.project,
                                       "branch": "branch-name",
                                       "topic": "topic-name",
                                       "id": "Ideadbeefdeadbeefdeadbeefdeadbe",
                                       "number": "123456",
                                       "subject": "Commit message subject",
                                       "owner": {"name": "Owner Name",
                                                 "email": "owner@example.com"},
                                       "url": "URL"},
                            "patchSet": {"number": "4",
                                         "revision": revision,
                                         "ref": fixture.ref,
                                         "uploader": {"name": "Uploader Name",
                                                      "email": "u@e.com"},
                                         "createdOn": 1342075181},
                            "uploader": {"name": "Uploader Name",
                                         "email": "uploader@example.com"}}
        gerrit.addEvent(patchset_created)
        comment_added = {"type": "comment-added",
                         "comment": " recheck no  bug   ",
                         "change": {"project": gerrit.project},
                         "patchSet": {"revision": revision,
                                      "ref": fixture.ref}}
        gerrit.addEvent(comment_added)
        gerrit.addEvent(None)
        gerrit.loop()
        mock_startWatching.assert_called()

        e = []
        e = e + [mock.call(gerrit.project, revision,
                           gerrit.banner,
                           {'verified': '0'}),
                 mock.call(gerrit.project, revision,
                           mock.ANY,
                           {'verified': '+1'})]
        e = e + [mock.call(gerrit.project, revision,
                           gerrit.banner,
                           {'verified': '0'}),
                 mock.call(gerrit.project, revision,
                           mock.ANY,
                           {'verified': '+1'})]
        self.assertEqual(mock_review.call_args_list, e)
        self.assertIn('THEREF', mock_review.call_args_list[1][0][2])
        self.assertIn('recheck', mock_review.call_args_list[3][0][2])
        os.path.exists(os.path.join(downstream, fixture.file_only_in_ref))

    @mock.patch.object(main.GerritExec, 'git_url')
    @mock.patch.object(main.GerritExec, 'review')
    def test_fail_clone(self, mock_review, mock_git_url):
        fixture = self.useFixture(GitFixture())
        downstream = os.path.join(fixture.path, "downstream")
        script = 'true'
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=1200,
                                                    username='USERNAME',
                                                    directory=downstream,
                                                    script=script,
                                                    project='project-name',
                                                    verbose=True))
        revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadb"
        event = {"type": "patchset-created",
                 "change": {"project": gerrit.project},
                 "patchSet": {"revision": revision,
                              "ref": fixture.ref}}
        mock_git_url.side_effect = lambda event: "INVALIDURL"
        gerrit.patchset_created(event)
        mock_review.assert_called_with(gerrit.project, revision,
                                       mock.ANY, {'verified': '-1'})
        args, kwargs = mock_review.call_args
        self.assertIn('INVALIDURL', args[2])

    @mock.patch.object(main.GerritExec, 'git_url')
    @mock.patch.object(main.GerritExec, 'review')
    def test_patchset_created(self, mock_review, mock_git_url):
        fixture = self.useFixture(GitFixture())
        downstream = os.path.join(fixture.path, "downstream")
        script = 'echo -n NOK && false'
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=1200,
                                                    username='USERNAME',
                                                    directory=downstream,
                                                    script=script,
                                                    project='project-name',
                                                    verbose=True))
        revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadb"
        event = {"type": "patchset-created",
                 "change": {"project": gerrit.project},
                 "patchSet": {"revision": revision,
                              "ref": fixture.ref}}
        mock_git_url.side_effect = lambda event: fixture.url
        gerrit.patchset_created(event)
        mock_review.assert_called_with(gerrit.project, revision,
                                       mock.ANY, {'verified': '-1'})
        args, kwargs = mock_review.call_args
        assert args[2].index('NOK')

    @mock.patch.object(main.GerritExec, 'git_url')
    @mock.patch.object(main.GerritExec, 'review')
    def test_timeout(self, mock_review, mock_git_url):
        fixture = self.useFixture(GitFixture())
        downstream = os.path.join(fixture.path, "downstream")
        script = 'bash -c "set -x ; sleep 3600" # '
        timeout = 1
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=timeout,
                                                    username='USERNAME',
                                                    directory=downstream,
                                                    script=script,
                                                    project='project-name',
                                                    verbose=True))
        revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadb"
        event = {"type": "patchset-created",
                 "change": {"project": gerrit.project},
                 "patchSet": {"revision": revision,
                              "ref": fixture.ref}}
        mock_git_url.side_effect = lambda event: fixture.url
        gerrit.patchset_created(event)
        mock_review.assert_called_with(gerrit.project, revision,
                                       mock.ANY, {'verified': '-1'})
        args, kwargs = mock_review.call_args
        assert args[2].index('sleep 3600')

    @mock.patch.object(main.GerritExec, 'git_url')
    @mock.patch.object(main.GerritExec, 'review')
    def test_comment_added_recheck(self, mock_review, mock_git_url):
        fixture = self.useFixture(GitFixture())
        downstream = os.path.join(fixture.path, "downstream")
        script = 'true'
        timeout = 1
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=timeout,
                                                    username='USERNAME',
                                                    directory=downstream,
                                                    script=script,
                                                    project='project-name',
                                                    verbose=True))
        revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadb"
        event = {"type": "comment-added",
                 "comment": " recheck  no  bug   ",
                 "change": {"project": gerrit.project},
                 "patchSet": {"revision": revision,
                              "ref": fixture.ref}}
        mock_git_url.side_effect = lambda event: fixture.url
        gerrit.comment_added(event)
        mock_review.assert_called_with(gerrit.project, revision,
                                       mock.ANY, {'verified': '+1'})

    @mock.patch.object(main.GerritExec, 'git_url')
    @mock.patch.object(main.GerritExec, 'review')
    def test_comment_added_run(self, mock_review, mock_git_url):
        fixture = self.useFixture(GitFixture())
        downstream = os.path.join(fixture.path, "downstream")
        script = 'true'
        timeout = 1
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=timeout,
                                                    username='USERNAME',
                                                    directory=downstream,
                                                    script=script,
                                                    project='project-name',
                                                    verbose=True))
        revision = "deadbeefdeadbeefdeadbeefdeadbeefdeadb"
        event = {"type": "comment-added",
                 "comment": "Patch 4: \n\n this is run gerritexec   ",
                 "change": {"project": gerrit.project},
                 "patchSet": {"revision": revision,
                              "ref": fixture.ref}}
        mock_git_url.side_effect = lambda event: fixture.url
        gerrit.comment_added(event)
        mock_review.assert_called_with(gerrit.project, revision,
                                       mock.ANY, {'verified': '+1'})

    def test_git_url(self):
        gerrit = main.GerritExec(argparse.Namespace(hostname='HOST',
                                                    keyfile='id_rsa',
                                                    port=29418,
                                                    timeout=1200,
                                                    username='USERNAME',
                                                    directory='DOWNSTREAM',
                                                    script='SCRIPT',
                                                    project='project-name',
                                                    verbose=True))
        event = {"change": {"project": gerrit.project}}
        url = gerrit.git_url(event)
        self.assertIn(gerrit.project, url)
        self.assertIn(gerrit.hostname, url)
