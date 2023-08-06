#
# This file is part of Gruvi. Gruvi is free software available under the
# terms of the MIT license. See the file "LICENSE" that was provided
# together with this source file for the licensing terms.
#
# Copyright (c) 2012-2014 the Gruvi authors. See the file "AUTHORS" for a
# complete list.

from __future__ import absolute_import, print_function

import os
import sys
import time
import signal
import locale
import pyuv
import pkg_resources

import gruvi
from gruvi.hub import get_hub
from gruvi.errors import Timeout
from gruvi.process import Process, PIPE, DEVNULL
from gruvi.stream import StreamClient

from support import UnitTest, unittest


def create_cmd_wrappers(bindir):
    """On Windows, Create executable file wrappers for our utilities in tests/bin."""
    # This is relevant on Windows only. On Unix our utilities can be executed
    # by uv_spawn() directly.
    #
    # On Windows, a simple solution could be to create .bat file wrappers.
    # However that doesn't work because uv_spawn() uses CreateProcess() which
    # only supports .exe and .com files.
    #
    # The solution is to create little .exe wrapper for each program.
    # Fortunately this is easy. Setuptools contains such a wrapper as a package
    # resource. We need to copy it, and create a basename-script.py wrapper.
    if not sys.platform.startswith('win'):
        return
    shebang = '#!{0}\r\n'.format(sys.executable)
    wrapper = pkg_resources.resource_string('setuptools', 'cli.exe')
    for fname in os.listdir(bindir):
        if '.' in fname:
            continue
        absname = os.path.join(bindir, fname)
        scriptname = absname + '-script.py'
        exename = absname + '.exe'
        if os.access(scriptname, os.R_OK) and os.access(exename, os.X_OK):
            continue
        with open(absname) as fin:
            lines = [line.rstrip() + '\r\n' for line in fin.readlines()]
            lines[0] = shebang
        with open(scriptname, 'w') as fout:
            fout.writelines(lines)
        with open(exename, 'wb') as fout:
            fout.write(wrapper)


def python_script(args):
    """On Windows, modify *args* so that a script in test/bin is executed
    directly via Python rather than via the .exe wrapper."""
    # This is needed to make inheriting of handles other than stdio work. My
    # assumption is that the .exe wrapper is not passing on these handles (or
    # that they are somehow not inheritable).
    if not sys.platform.startswith('win'):
        return args
    if isinstance(args, str):
        args = [args]
    args[0] = 'bin\\{0}'.format(args[0])
    return [sys.executable] + args


class TestProcess(UnitTest):

    @classmethod
    def setUpClass(cls):
        super(TestProcess, cls).setUpClass()
        bindir = os.path.join(cls.testdir, 'bin')
        create_cmd_wrappers(bindir)
        path = os.environ.get('PATH', '')
        if bindir not in path:
            os.environ['PATH'] = os.pathsep.join([bindir, path])

    def test_spawn(self):
        # Ensure that spawning a child works.
        proc = Process()
        proc.spawn('true')
        self.assertIsInstance(proc.pid, int)
        proc.wait()
        self.assertEqual(proc.returncode, 0)

    def test_respawn(self):
        # Ensure that calling spawn() again after the child has exited works.
        proc = Process()
        proc.spawn('true')
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        proc.spawn('false')
        proc.wait()
        self.assertEqual(proc.returncode, 1)

    def test_spawn_shell(self):
        # Ensure spawning a child with shell=True works.
        proc = Process()
        proc.spawn('true', shell=True)
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        proc.spawn('false', shell=True)
        proc.wait()
        self.assertEqual(proc.returncode, 1)

    def test_spawn_args(self):
        # Ensure that passing arguments to our child works.
        proc = Process()
        proc.spawn(['exitn', '1', '2', '3'])
        proc.wait()
        self.assertEqual(proc.returncode, 6)

    def test_spawn_shell_args(self):
        # Ensure that passing arguments to our child works with shell=True.
        proc = Process()
        proc.spawn('exitn 1 2 3', shell=True)
        proc.wait()
        self.assertEqual(proc.returncode, 6)

    def test_spawn_executable(self):
        # Ensure that spawn honors the executable argument.
        proc = Process()
        proc.spawn(['exit', '1'], executable='true')
        proc.wait()
        self.assertEqual(proc.returncode, 0)

    def test_spawn_shell_executable(self):
        # Ensure that spawn honors the executable argument with shell=True.
        proc = Process()
        proc.spawn(['exit 1'], shell=True, executable='echo', stdout=PIPE)
        output = proc.stdout.readline().split()
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(output[0], b'-c' if hasattr(os, 'fork') else b'/c')
        self.assertEqual(output[1], b'exit')
        self.assertEqual(output[2], b'1')

    def test_exit(self):
        # Ensure that the child's exist status is correctly reported.
        proc = Process()
        proc.spawn(['exitn', '5'])
        proc.wait()
        self.assertEqual(proc.returncode, 5)

    def test_spawn_cwd(self):
        # Ensure that the "cwd" argument to spawn is effective.
        proc = Process()
        encoding = locale.getpreferredencoding()
        curdir = os.getcwd()
        tempdir = self.tempdir
        self.assertNotEqual(tempdir, curdir)
        proc.spawn('pwd', stdout=PIPE)
        childdir = proc.stdout.readline().rstrip().decode(encoding)
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(childdir, curdir)
        proc.spawn('pwd', stdout=PIPE, cwd=tempdir)
        childdir = proc.stdout.readline().rstrip().decode(encoding)
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(childdir, tempdir)

    def test_spawn_env(self):
        # Ensure that the "env" argument to spawn is effective.
        proc = Process()
        encoding = locale.getpreferredencoding()
        env = os.environ.copy()
        env['FOO'] = 'Bar'
        self.assertNotEqual(os.environ.get('FOO'), env['FOO'])
        proc.spawn(['echo', '$FOO'], stdout=PIPE, env=env)
        value = proc.stdout.readline().rstrip().decode(encoding)
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(value, env['FOO'])

    def test_poll(self):
        # Ensure that poll() checks if the child is still alive.
        proc = Process()
        proc.spawn(['sleep', '0.2'])
        tries = 0
        while True:
            if proc.poll() is not None:
                break
            tries += 1
            gruvi.sleep(0.02)
        self.assertEqual(proc.returncode, 0)
        self.assertGreater(tries, 5)

    def test_wait(self):
        # Ensure that wait() waits for the child to exit.
        proc = Process()
        t0 = time.time()
        proc.spawn(['sleep', '0.2'])
        proc.wait()
        t1 = time.time()
        self.assertGreater(t1-t0, 0.2)
        self.assertEqual(proc.returncode, 0)

    def test_stdout(self):
        # Ensure that it's possible to capure stdout using stdout=PIPE
        proc = Process()
        proc.spawn('catn', stdin=PIPE, stdout=PIPE)
        proc.stdin.write(b'Foo\n')
        proc.stdin.close()
        self.assertEqual(proc.stdout.readline(), b'Foo\n')
        self.assertEqual(proc.stdout.readline(), b'')
        proc.wait()
        self.assertEqual(proc.returncode, 0)

    def test_stderr(self):
        # Ensure that it's possible to capure stderr using stderr=PIPE
        proc = Process()
        proc.spawn(['catn', '0', '2'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        proc.stdin.write(b'Foo\n')
        proc.stdin.close()
        self.assertEqual(proc.stderr.readline(), b'Foo\n')
        self.assertEqual(proc.stderr.readline(), b'')
        self.assertEqual(proc.stdout.readline(), b'')
        proc.wait()
        self.assertEqual(proc.returncode, 0)

    def test_devnull(self):
        # Ensure that using stdout=DEVNULL doesn't produce any output.
        proc = Process()
        proc.spawn('catn', stdin=PIPE, stdout=DEVNULL)
        proc.stdin.write(b'Foo\n')
        proc.stdin.close()
        self.assertIsNone(proc.stdout)
        proc.wait()
        self.assertEqual(proc.returncode, 0)

    def test_stdio_encoding(self):
        # Ensure that passing encoding=xxx to the constructor works.
        encoding = locale.getpreferredencoding()
        proc = Process(encoding=encoding)
        proc.spawn('catn', stdin=PIPE, stdout=PIPE)
        proc.stdin.write(u'20 \u20ac\n')
        proc.stdin.close()
        self.assertEqual(proc.stdout.readline(), u'20 \u20ac\n')
        self.assertEqual(proc.wait(), 0)

    def test_spawn_unicode_args(self):
        # Ensure that it's possible to spawn a child with unicode arguments.
        proc = Process()
        env = os.environ.copy()
        # Ensure to have a capable sys.stdout encoding.
        env['PYTHONIOENCODING'] = 'utf-8'
        proc.spawn(['echo', 'foo', u'\u20ac'], stdout=PIPE, env=env)
        # Unsure why a \x00 is present at the end
        line = proc.stdout.readline().rstrip()
        self.assertEqual(line, u'foo \u20ac'.encode('utf-8'))
        proc.wait()

    def test_spawn_unicode_env(self):
        # Ensure that it's possible to spawn a child with a unicode environment.
        proc = Process()
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['FOO'] = u'foo \u20ac'
        proc.spawn(['echo', '$FOO'], stdout=PIPE, env=env)
        line = proc.stdout.readline().rstrip()
        self.assertEqual(line, u'foo \u20ac'.encode('utf-8'))
        proc.wait()

    def test_timeout(self):
        # Ensure that the timeout=xxx constructor argument works.
        proc = Process(timeout=0.1)
        proc.spawn('catn', stdin=PIPE, stdout=PIPE)
        self.assertRaises(Timeout, proc.stdout.readline)
        proc.stdin.write(b'foo\n')
        self.assertEqual(proc.stdout.readline(), b'foo\n')
        proc.stdin.close()
        self.assertEqual(proc.wait(), 0)

    def test_inherit_handle(self):
        # Ensure that it's possible to pass a handle to the child.
        # Note: The "ipc" flag doubles as a read/write flag.
        hub = get_hub()
        handle = pyuv.Pipe(hub.loop, True)
        proc = Process()
        proc.spawn(python_script(['catn', '3']), extra_handles=[handle])
        stream = StreamClient()
        stream.connect(handle)
        stream.write(b'Foo\n')
        self.assertEqual(stream.readline(), b'Foo\n')
        stream.write_eof()
        self.assertEqual(stream.readline(), b'')
        stream.close()
        proc.wait()
        self.assertEqual(proc.returncode, 0)

    def test_send_signal(self):
        # Ensure we can send a signal to our child using send_signal(0
        proc = Process()
        proc.spawn(['sleep', '1'])
        proc.send_signal(signal.SIGINT)
        proc.wait()
        self.assertEqual(proc.returncode, -signal.SIGINT)

    def test_terminate(self):
        # Ensure that terminate() kills our child.
        proc = Process()
        proc.spawn(['sleep', '1'])
        proc.terminate()
        proc.wait()
        self.assertEqual(proc.returncode, -signal.SIGTERM)

    def test_kill(self):
        # Ensure that kill() kills our child.
        proc = Process()
        proc.spawn(['sleep', '1'])
        proc.kill()
        proc.wait()
        # Windows does not have signal.SIGKILL
        self.assertEqual(proc.returncode, -9)

    def test_child_exited(self):
        # Ensure that the child_exited callback gets called.
        proc = Process()
        cbargs = []
        def on_child_exit(*args):
            cbargs.extend(args)
        proc.child_exited = on_child_exit
        proc.spawn(['sleep', '0'])
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(cbargs[0], 0)
        self.assertEqual(cbargs[1], 0)

    def test_send_data(self):
        # Test that sending a lot of data works.
        proc = Process()
        proc.spawn('catn', stdin=PIPE, stdout=PIPE)
        buf = b'x' * 1024
        nbytes = 10*1024*1024  # Send 10MB
        result = [0, 0]
        def writer():
            while result[0] < nbytes:
                towrite = min(1024, nbytes - result[0])
                proc.stdin.write(buf[:towrite])
                result[0] += towrite
            proc.stdin.flush()
            proc.stdin.write_eof()
        def reader():
            while True:
                read = len(proc.stdout.read1(1024))
                if read == 0:
                    break
                result[1] += read
        gruvi.spawn(writer)
        gruvi.spawn(reader)
        proc.wait()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result[0], nbytes)
        self.assertEqual(result[1], nbytes)


if __name__ == '__main__':
    unittest.main()
