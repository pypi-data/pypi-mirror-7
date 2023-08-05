#!/usr/bin/env python
#
# $Id: test_sendfile.py 109 2012-01-12 19:09:48Z g.rodola@gmail.com $
#

# ======================================================================
# This software is distributed under the MIT license reproduced below:
#
#     Copyright (C) 2009-2012  Giampaolo Rodola' <g.rodola@gmail.com>
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Giampaolo Rodola' not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# Giampaolo Rodola' DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT Giampaolo Rodola' BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================

"""
pysendfile test suite; works with both python 2.x and 3.x (no need
to run 2to3 tool first).
Accepts a -k cmdline option to avoid removing the big file created
during tests.
"""

from __future__ import with_statement

import unittest
import os
import sys
import socket
import asyncore
import asynchat
import threading
import errno
import time
import atexit
import warnings
import optparse

import sendfile

PY3 = sys.version_info >= (3,)

def b(x):
    if PY3:
        return bytes(x, 'ascii')
    return x

TESTFN = "$testfile"
TESTFN2 = TESTFN + "2"
TESTFN3 = TESTFN + "3"
DATA = b("12345abcde" * 1024 * 1024)  # 10 Mb
HOST = '127.0.0.1'
BIGFILE_SIZE = 2500000000  # > 2GB file (2GB = 2147483648 bytes)
BUFFER_LEN = 4096

try:
    sendfile.sendfile(0, 0, 0, 0, 0)
except TypeError:
    SUPPORT_HEADER_TRAILER = False
except Exception:
    SUPPORT_HEADER_TRAILER = True

def safe_remove(file):
    try:
        os.remove(file)
    except OSError:
        pass

def has_large_file_support():
    # taken from Python's Lib/test/test_largefile.py
    with open(TESTFN, 'wb', buffering=0) as f:
        try:
            f.seek(BIGFILE_SIZE)
            # seeking is not enough of a test: you must write and flush too
            f.write(b('x'))
            f.flush()
        except (IOError, OverflowError):
            return False
        else:
            return True


class Handler(asynchat.async_chat):
    ac_in_buffer_size = BUFFER_LEN
    ac_out_buffer_size = BUFFER_LEN

    def __init__(self, conn):
        asynchat.async_chat.__init__(self, conn)
        self.in_buffer = []
        self.closed = False
        self.push(b("220 ready\r\n"))

    def handle_read(self):
        data = self.recv(BUFFER_LEN)
        self.in_buffer.append(data)

    def get_data(self):
        return b('').join(self.in_buffer)

    def handle_close(self):
        self.close()

    def close(self):
        asynchat.async_chat.close(self)
        self.closed = True

    def handle_error(self):
        raise


class NoMemoryHandler(Handler):
    # same as above but doesn't store received data in memory
    ac_in_buffer_size = 65536

    def __init__(self, conn):
        Handler.__init__(self, conn)
        self.in_buffer_len = 0

    def handle_read(self):
        data = self.recv(self.ac_in_buffer_size)
        self.in_buffer_len += len(data)

    def get_data(self):
        raise NotImplementedError


class Server(asyncore.dispatcher, threading.Thread):

    handler = Handler

    def __init__(self, address):
        threading.Thread.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(5)
        self.host, self.port = self.socket.getsockname()[:2]
        self.handler_instance = None
        self._active = False
        self._active_lock = threading.Lock()

    # --- public API

    @property
    def running(self):
        return self._active

    def start(self):
        assert not self.running
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    def stop(self):
        assert self.running
        self._active = False
        self.join()
        assert not asyncore.socket_map, asyncore.socket_map

    def wait(self):
        # wait for handler connection to be closed, then stop the server
        while not getattr(self.handler_instance, "closed", True):
            time.sleep(0.001)
        self.stop()

    # --- internals

    def run(self):
        self._active = True
        self.__flag.set()
        while self._active and asyncore.socket_map:
            self._active_lock.acquire()
            asyncore.loop(timeout=0.001, count=1)
            self._active_lock.release()
        asyncore.close_all()

    def handle_accept(self):
        conn, addr = self.accept()
        self.handler_instance = self.handler(conn)

    def handle_connect(self):
        self.close()
    handle_read = handle_connect

    def writable(self):
        return 0

    def handle_error(self):
        raise


def sendfile_wrapper(sock, file, offset, nbytes=BUFFER_LEN, header="", trailer=""):
    """A higher level wrapper representing how an application is
    supposed to use sendfile().
    """
    while 1:
        try:
            if SUPPORT_HEADER_TRAILER:
                sent = sendfile.sendfile(sock, file, offset, nbytes, header,
                                         trailer)
            else:
                sent = sendfile.sendfile(sock, file, offset, nbytes)
        except OSError:
            err = sys.exc_info()[1]
            if err.errno == errno.EAGAIN:  # retry
                continue
            raise
        else:
            assert sent <= nbytes, (sent, nbytes)
            return sent


class TestSendfile(unittest.TestCase):

    def setUp(self):
        self.server = Server((HOST, 0))
        self.server.start()
        self.client = socket.socket()
        self.client.connect((self.server.host, self.server.port))
        self.client.settimeout(1)
        # synchronize by waiting for "220 ready" response
        self.client.recv(1024)
        self.sockno = self.client.fileno()
        self.file = open(TESTFN, 'rb')
        self.fileno = self.file.fileno()

    def tearDown(self):
        safe_remove(TESTFN2)
        self.file.close()
        self.client.close()
        if self.server.running:
            self.server.stop()
        self.server = None  # allow garbage collection

    def test_send_whole_file(self):
        # normal send
        total_sent = 0
        offset = 0
        while 1:
            sent = sendfile_wrapper(self.sockno, self.fileno, offset)
            if sent == 0:
                break
            total_sent += sent
            offset += sent
            self.assertEqual(offset, total_sent)

        self.assertEqual(total_sent, len(DATA))
        self.client.close()
        if "sunos" in sys.platform:
            time.sleep(.1)
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(len(data), len(DATA))
        self.assertEqual(hash(data), hash(DATA))

    def test_send_from_certain_offset(self):
        # start sending a file at a certain offset
        total_sent = 0
        offset = int(len(DATA) / 2)
        while 1:
            sent = sendfile_wrapper(self.sockno, self.fileno, offset)
            if sent == 0:
                break
            total_sent += sent
            offset += sent

        self.client.close()
        if "sunos" in sys.platform:
            time.sleep(.1)
        self.server.wait()
        data = self.server.handler_instance.get_data()
        expected = DATA[int(len(DATA) / 2):]
        self.assertEqual(total_sent, len(expected))
        self.assertEqual(hash(data), hash(expected))

    if SUPPORT_HEADER_TRAILER:
        def test_header(self):
            total_sent = 0
            header = b("x") * 512
            sent = sendfile.sendfile(self.sockno, self.fileno, 0, header=header)
            total_sent += sent
            offset = BUFFER_LEN
            while 1:
                sent = sendfile_wrapper(self.sockno, self.fileno, offset)
                if sent == 0:
                    break
                offset += sent
                total_sent += sent

            expected_data = header + DATA
            self.assertEqual(total_sent, len(expected_data))
            self.client.close()
            self.server.wait()
            data = self.server.handler_instance.get_data()
            self.assertEqual(len(data), len(expected_data))
            self.assertEqual(hash(data), hash(expected_data))

        def test_trailer(self):
            with open(TESTFN2, 'wb') as f:
                f.write(b("abcde"))
            with open(TESTFN2, 'rb') as f:
                sendfile.sendfile(self.sockno, f.fileno(), 0,
                                  trailer=b("12345"))
                time.sleep(.1)
                self.client.close()
                self.server.wait()
                data = self.server.handler_instance.get_data()
                self.assertEqual(data, b("abcde12345"))

    def test_non_socket(self):
        fd_in = open(TESTFN, 'rb')
        fd_out = open(TESTFN2, 'wb')
        try:
            sendfile.sendfile(fd_in.fileno(), fd_out.fileno(), 0, BUFFER_LEN)
        except OSError:
            err = sys.exc_info()[1]
            self.assertEqual(err.errno, errno.EBADF)
        else:
            self.fail("exception not raised")
        finally:
            fd_in.close()
            fd_out.close()

    if sys.platform.startswith('freebsd'):
        def test_send_nbytes_0(self):
            # On Mac OS X and FreeBSD a value of 0 for nbytes
            # is supposed to send the whole file in one shot.
            # OSX implementation appears to be just broken.
            # On *BSD this works most of the times: sometimes
            # EAGAIN is returned internally and here we get the
            # number of bytes sent.
            sent = sendfile.sendfile(self.sockno, self.fileno, 0, 0)
            if sent == len(DATA):
                self.client.close()
                self.server.wait()
                data = self.server.handler_instance.get_data()
                self.assertEqual(len(data), len(DATA))
                self.assertEqual(hash(data), hash(DATA))

    if hasattr(sendfile, "SF_NODISKIO"):
        def test_flags(self):
            try:
                sendfile.sendfile(self.sockno, self.fileno, 0, BUFFER_LEN,
                                  flags=sendfile.SF_NODISKIO)
            except OSError:
                err = sys.exc_info()[1]
                if err.errno not in (errno.EBUSY, errno.EAGAIN):
                    raise

    # --- corner cases

    def test_offset_overflow(self):
        # specify an offset > file size
        offset = len(DATA) + BUFFER_LEN
        sent = sendfile.sendfile(self.sockno, self.fileno, offset, BUFFER_LEN)
        self.assertEqual(sent, 0)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(data, b(''))

    if "sunos" not in sys.platform:
        def test_invalid_offset(self):
            try:
                sendfile.sendfile(self.sockno, self.fileno, -1, BUFFER_LEN)
            except OSError:
                err = sys.exc_info()[1]
                self.assertEqual(err.errno, errno.EINVAL)
            else:
                self.fail("exception not raised")

    def test_small_file(self):
        data = b('foo bar')
        with open(TESTFN2, 'wb') as f:
            f.write(data)
        with open(TESTFN2, 'rb') as f:
            offset = 0
            while 1:
                sent = sendfile_wrapper(self.sockno, f.fileno(), offset)
                if sent == 0:
                    break
                offset += sent
            self.client.close()
            time.sleep(.1)
            self.server.wait()
            data_sent = self.server.handler_instance.get_data()
            self.assertEqual(data_sent, data)

    def test_small_file_and_offset_overflow(self):
        data = b('foo bar')
        with open(TESTFN2, 'wb') as f:
            f.write(data)
        with open(TESTFN2, 'rb') as f:
            sendfile_wrapper(self.sockno, f.fileno(), 4096)
            self.client.close()
            self.server.wait()
            data_sent = self.server.handler_instance.get_data()
            self.assertEqual(data_sent, b(''))

    def test_empty_file(self):
        data = b('')
        with open(TESTFN2, 'wb') as f:
            f.write(data)
        with open(TESTFN2, 'rb') as f:
            sendfile_wrapper(self.sockno, f.fileno(), 0)
            self.client.close()
            self.server.wait()
            data_sent = self.server.handler_instance.get_data()
            self.assertEqual(data_sent, data)

    if "linux" in sys.platform:
        def test_offset_none(self):
            # on Linux offset == None sendfile() call is supposed
            # to update the file offset
            while 1:
                sent = sendfile_wrapper(self.sockno, self.fileno, None)
                if sent == 0:
                    break
            self.client.close()
            self.server.wait()
            data = self.server.handler_instance.get_data()
            self.assertEqual(len(data), len(DATA))
            self.assertEqual(hash(data), hash(DATA))


class RepeatedTimer:

    def __init__(self, timeout, fun):
        self.timeout = timeout
        self.fun = fun

    def start(self):
        def main():
            self.fun()
            self.start()
        self.timer = threading.Timer(1, main)
        self.timer.start()

    def stop(self):
        self.timer.cancel()


class TestLargeFile(unittest.TestCase):

    def setUp(self):
        self.server = Server((HOST, 0))
        self.server.handler = NoMemoryHandler
        self.server.start()
        self.client = socket.socket()
        self.client.connect((self.server.host, self.server.port))
        self.client.settimeout(1)
        # synchronize by waiting for "220 ready" response
        self.client.recv(1024)
        self.sockno = self.client.fileno()
        sys.stdout.write("\ncreating file:\n")
        sys.stdout.flush()
        self.create_file()
        self.file = open(TESTFN3, 'rb')
        self.fileno = self.file.fileno()
        sys.stdout.write("\nstarting transfer:\n")
        sys.stdout.flush()

    def tearDown(self):
        if hasattr(self, 'file'):
            self.file.close()
        self.client.close()
        if self.server.running:
            self.server.stop()

    def print_percent(self, a, b):
        percent = ((a * 100) / b)
        sys.stdout.write("\r%2d%%" % percent)
        sys.stdout.flush()

    def create_file(self):
        if os.path.isfile(TESTFN3) and os.path.getsize(TESTFN3) >= BIGFILE_SIZE:
            return
        f = open(TESTFN3, 'wb')
        chunk_len = 65536
        chunk = b('x' * chunk_len)
        total = 0
        timer = RepeatedTimer(1, lambda: self.print_percent(total, BIGFILE_SIZE))
        timer.start()
        try:
            while 1:
                f.write(chunk)
                total += chunk_len
                if total >= BIGFILE_SIZE:
                    break
        finally:
            f.close()
            timer.stop()

    def test_big_file(self):
        total_sent = 0
        offset = 0
        nbytes = 65536
        file_size = os.path.getsize(TESTFN3)
        timer = RepeatedTimer(1, lambda: self.print_percent(total_sent,
                                                            file_size))
        timer.start()
        try:
            while 1:
                sent = sendfile_wrapper(self.sockno, self.fileno, offset,
                                        nbytes)
                if sent == 0:
                    break
                total_sent += sent
                offset += sent
                self.assertEqual(offset, total_sent)
        except Exception:
            print
            raise
        finally:
            sys.stdout.write("\n")
            sys.stdout.flush()
            timer.stop()

        self.assertEqual(total_sent, file_size)
        self.client.close()
        if "sunos" in sys.platform:
            time.sleep(1)
        self.server.wait()
        data_len = self.server.handler_instance.in_buffer_len
        file_size = os.path.getsize(TESTFN3)
        self.assertEqual(file_size, data_len)


def test_main():
    parser = optparse.OptionParser()
    parser.add_option('-k', '--keepfile', action="store_true", default=False,
                      help="do not remove test big file on exit")
    options, args = parser.parse_args()
    if not options.keepfile:
        atexit.register(lambda: safe_remove(TESTFN3))

    def cleanup():
        safe_remove(TESTFN)
        safe_remove(TESTFN2)

    atexit.register(cleanup)

    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSendfile))
    if has_large_file_support():
        test_suite.addTest(unittest.makeSuite(TestLargeFile))
    else:
        atexit.register(warnings.warn, "large files unsupported", RuntimeWarning)
    cleanup()
    with open(TESTFN, "wb") as f:
        f.write(DATA)
    unittest.TextTestRunner(verbosity=2).run(test_suite)

if __name__ == '__main__':
    test_main()
