# -*- coding: utf-8 -*-
# Copyright (C) 2013  Fabio Falcinelli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#SocketServer has been renamed in python3 to socketserver
import os
import socket
import subprocess
import sys

import pydivert


try:
    from socketserver import ThreadingMixIn, TCPServer, UDPServer, BaseRequestHandler
except ImportError:
    from SocketServer import ThreadingMixIn, TCPServer, UDPServer, BaseRequestHandler

__author__ = 'fabio'


class EchoUpperTCPHandler(BaseRequestHandler):
    """
    Simple TCP request handler returning data to uppercase.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(4096).strip()
        # just send back the same data, but upper-cased
        # print self.data
        self.request.sendall(self.data.upper())


class EchoUpperUDPHandler(BaseRequestHandler):
    """
    Simple UDP request handler returning data to uppercase.
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # print "{} wrote:".format(self.client_address[0])
        # print data
        socket.sendto(data.upper(), self.client_address)


class FakeTCPServerIPv4(ThreadingMixIn, TCPServer):
    allow_reuse_address = True

    def __str__(self):
        return "FakeTCPServerIPv4 listening on %s" % self.server_address


class FakeTCPServerIPv6(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    address_family = socket.AF_INET6

    def __str__(self):
        return "FakeTCPServerIPv6 listening on %s" % self.server_address


class FakeUDPServer(ThreadingMixIn, UDPServer):
    allow_reuse_address = True

    def __str__(self):
        return "FakeUDPServer listening on %s" % self.server_address


class FakeTCPClient():
    def __init__(self, connect_address, message, ipv6=False):
        self.connect_addr = connect_address
        self.message = message
        self.ipv6 = ipv6

    def send(self):
        sock = socket.socket(socket.AF_INET if not self.ipv6 else socket.AF_INET6, socket.SOCK_STREAM)
        try:
            sock.connect(self.connect_addr)
            sock.sendall(self.message)
            self.response = sock.recv(4096)
        except Exception as e:
            pass
        finally:
            sock.close()


class FakeUDPClient():
    def __init__(self, connect_address, message, ipv6=False):
        self.connect_addr = connect_address
        self.message = message
        self.ipv6 = ipv6

    def send(self):
        sock = socket.socket(socket.AF_INET if not self.ipv6 else socket.AF_INET6, socket.SOCK_DGRAM)
        try:
            sock.sendto(self.message, self.connect_addr)
            self.response = sock.recv(4096)
        finally:
            sock.close()


def random_free_port(family=socket.AF_INET, type=socket.SOCK_STREAM):
    """
    Pick a free port in the given range
    """
    s = socket.socket(family, type)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", 0))
        return s.getsockname()[1]
    finally:
        s.close()


def run_test_suites():
    import unittest
    from unittest.test import loader
    from pydivert.tests.test_windivert import WinDivertTestCase, WinDivertTCPIPv4TestCase, WinDivertTCPIPv6TestCase
    from pydivert.tests.test_windivert import WinDivertUDPTestCase, WinDivertTCPDataCaptureTestCase, \
        WinDivertExternalInterfaceTestCase
    from pydivert.tests.test_windivert import WinDivertAsyncTestCase
    from pydivert.tests.test_winutils import WinInetTestCase
    from pydivert.tests import test_winutils

    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()

    for version in ("1.0", "1.1"):
        driver_dir = os.path.join(os.path.dirname(pydivert.__file__), os.pardir, "lib", version)
        if not os.path.exists(driver_dir):
            sys.stderr.write("Could not find directory %s\n" % driver_dir)
            sys.stderr.write("Tests for version %s will be skipped...\n" % version)
            continue

        with open(os.devnull, 'wb') as devnull:
            print("Preparing test environment for WinDivert version %s" % version)
            subprocess.call(['sc', 'stop', 'WinDivert%s' % version], stdout=devnull, stderr=devnull)
            subprocess.call(['sc', 'delete', 'WinDivert%s' % version], stdout=devnull, stderr=devnull)

        for test_class in [WinDivertTestCase,
                           WinDivertTCPIPv4TestCase,
                           WinDivertTCPIPv6TestCase,
                           WinDivertUDPTestCase,
                           WinDivertTCPDataCaptureTestCase,
                           WinDivertExternalInterfaceTestCase,
                           WinDivertAsyncTestCase]:
            tests = loader.loadTestsFromTestCase(test_class)
            for t in tests:
                t.version = version
            suite.addTests(tests)

    suite.addTests(loader.loadTestsFromTestCase(WinInetTestCase))
    runner.run(suite)


