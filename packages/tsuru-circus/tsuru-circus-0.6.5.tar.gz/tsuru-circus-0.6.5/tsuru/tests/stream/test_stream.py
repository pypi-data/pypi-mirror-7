# Copyright 2014 tsuru-circus authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import unittest
import mock
import os
import json

from tsuru.stream import Stream


class StreamTestCase(unittest.TestCase):
    def setUp(self):
        l_out = '2012-11-06 17:13:55 [12019] [INFO] Starting gunicorn 0.15.0\n'
        l_err = '2012-11-06 17:13:55 [12019] [ERROR] Error starting gunicorn\n'
        self.data = {}
        self.data['stderr'] = {
            'pid': 12018,
            'data': l_err,
            'name': 'stderr'
        }
        self.data['stdout'] = {
            'pid': 12018,
            'data': l_out,
            'name': 'stdout'
        }
        self.stream = Stream(watcher_name='mywatcher')
        self.stream.apprc = os.path.join(os.path.dirname(__file__),
                                         "testdata/apprc")

    def test_should_have_the_close_method(self):
        self.assertTrue(hasattr(Stream, "close"))

    @mock.patch("requests.post")
    def test_should_send_log_to_tsuru(self, post):
        post.return_value = mock.Mock(status_code=200)
        self.stream(self.data['stdout'])
        (appname, host, token, syslog_server,
         syslog_port, syslog_facility, syslog_socket) = self.stream.load_envs()
        url = "{0}/apps/{1}/log?source=mywatcher".format(host, appname)
        expected_msg = "Starting gunicorn 0.15.0\n"
        expected_data = json.dumps([expected_msg])
        post.assert_called_with(url, data=expected_data,
                                headers={"Authorization": "bearer " + token},
                                timeout=2)

    @mock.patch("logging.getLogger")
    @mock.patch('logging.handlers.SysLogHandler')
    @mock.patch('logging.info')
    def test_should_send_log_to_syslog_as_info(self, l_info,
                                               s_handler, logger):
        self.stream(self.data['stdout'])
        (appname, host, token, syslog_server,
         syslog_port, syslog_facility, syslog_socket) = self.stream.load_envs()
        my_logger = logger(appname)
        log_handler = s_handler(address=(syslog_server, syslog_port),
                                facility=syslog_facility,
                                socktype=syslog_socket)
        expected_msg = "Starting gunicorn 0.15.0\n"
        my_logger.addHandler(log_handler)
        l_info.assert_called_with(expected_msg)

    @mock.patch("logging.getLogger")
    @mock.patch('logging.handlers.SysLogHandler')
    @mock.patch('logging.error')
    def test_should_send_log_to_syslog_as_error(self, l_error,
                                                s_handler, logger):
        self.stream(self.data['stderr'])
        (appname, host, token, syslog_server,
         syslog_port, syslog_facility, syslog_socket) = self.stream.load_envs()
        my_logger = logger(appname)
        log_handler = s_handler(address=(syslog_server, syslog_port),
                                facility=syslog_facility,
                                socktype=syslog_socket)
        expected_msg = "Error starting gunicorn\n"
        my_logger.addHandler(log_handler)
        l_error.assert_called_with(expected_msg)

    @mock.patch("requests.post")
    def test_timeout_is_configurable(self, post):
        post.return_value = mock.Mock(status_code=200)
        stream = Stream(watcher_name="watcher", timeout=10)
        stream.apprc = os.path.join(os.path.dirname(__file__),
                                    "testdata/apprc")
        stream(self.data['stdout'])
        (appname, host, token, syslog_server,
         syslog_port, syslog_facility, syslog_socket) = self.stream.load_envs()
        url = "{0}/apps/{1}/log?source=watcher".format(host, appname)
        expected_msg = "Starting gunicorn 0.15.0\n"
        expected_data = json.dumps([expected_msg])
        post.assert_called_with(url, data=expected_data,
                                headers={"Authorization": "bearer " + token},
                                timeout=10)

    @mock.patch("requests.post")
    def test_should_ignore_errors_in_post_call(self, post):
        post.side_effect = Exception()
        self.stream(self.data['stdout'])

    @mock.patch("tsuru.common.load_envs")
    def test_should_slience_errors_when_envs_does_not_exist(lenvs, self):
        lenvs.return_value = {}
        try:
            stream = Stream()
            stream(self.data['stdout'])
        except Exception as e:
            msg = "Should not fail when envs does not exist. " \
                  "Exception: {}".format(e)
            self.fail(msg)
