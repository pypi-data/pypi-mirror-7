import json
import logging
import os
import time
import itertools
import functools
import select
from subprocess import Popen, PIPE


DEVNULL = open(os.devnull, 'w+b')


def print_prepare(arg):
    return json.dumps(arg) if ' ' in arg else arg


class SubprocessExecutionException(Exception):
    """ Raised by the Process class if subprocess finished with exit_code != 0
    User error message is constructed from cmd_line and stderr or stdout.
    """
    def __init__(self, proc, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.proc = proc


class _ProcOutput(object):
    def __init__(self, file_path=None, line_callback=None):
        self._w_handle = None
        self._r_handle = None
        self.mode = 'wb'
        self._unhandled_line_part = ''
        self.file_path = file_path
        self.line_callback = line_callback

    def get_lines(self):
        if not self.file_path:
            return []
        with open(self.file_path) as f:
            return f.readlines()

    def get_string(self):
        return ''.join(self.get_lines())

    def _get_popen_param(self):
        if self.file_path:
            self._w_handle = open(self.file_path, self.mode)
            if self.line_callback:
                self._r_handle = open(self.file_path)
            return self._w_handle
        return DEVNULL

    def _close(self):
        if self._w_handle:
            self._w_handle.close()
        if self._r_handle:
            self._r_handle.close()

    def _callback(self, ready_handle_list):
        if not self._r_handle in ready_handle_list:
            return
        lines = self._r_handle.read().splitlines(True)
        if not lines:
            return
        lines[0] = self._unhandled_line_part + lines[0]
        if not lines[-1].endswith(('\n', '\r', '\r\n')):
            self._unhandled_line_part = lines.pop()
        for line in lines:
            self.line_callback(line)


def _get_stdin_popen_param(proc):
    if not proc.stdin:
        return DEVNULL
    if isinstance(proc.stdin, basestring):
        return open(proc.stdin)
    if isinstance(proc.stdin, (list, tuple)):
        return PIPE
    raise Exception('Bad stdin: %s', proc.stdin)


class Process(object):
    """ Use this class to run external processes. Example:
    >>> p = Process('python', '-c', 'x,y=input(),input(); print x+y', stdin=['2', '2']).run()
    >>> p.stdout.get_string()
    4

    Passing positional arguments to __init__ is same as using add_arg(*args).

    kwargs: stdin
    >>> Process('wc', stdin='/path/to/file').run() # /path/to/file will be streamed to wc stdin
    >>> Process('wc', stdin=['first line', 'second line']) # pass list to stdin line by line

    kwargs: stdout and stderr
    >>> money_lines = []
    >>> Process('grep', r'\$\d+', stdin='file.txt', stdout=lambda line: money_lines.append(line)).run() # pass callable
    >>> Process('wc', 'file.txt', stderr='errors.log')

    You can also set these using process.[stdout|stderr].line_parser and process.[stdout|stderr].file_path
    """
    _ids = itertools.count(0)

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id') or 'process_%s' % Process._ids.next()
        self.popen = None
        self.cwd = kwargs.get('cwd')
        self.args = []
        self.add_arg(*args)

        self.stdin = kwargs.get('stdin')

        self.stderr = _ProcOutput()
        stderr = kwargs.get('stderr', True)
        if stderr:
            self.stderr.file_path = stderr if isinstance(stderr, basestring) else '%s.err' % self.id
            if callable(stderr):
                self.stderr.line_callback = stderr

        self.stdout = _ProcOutput()
        stdout = kwargs.get('stdout', True)
        if stdout:
            self.stdout.file_path = stdout if isinstance(stdout, basestring) else '%s.out' % self.id
            if callable(stdout):
                self.stdout.line_callback = stdout

    def run(self, wait=True):
        """ Run the process. If wait is true, wait for it to finish and parse output if line parsers are supplied. """
        try:
            stdout = self.stdout._get_popen_param()
            stderr = self.stderr._get_popen_param()
            stdin = _get_stdin_popen_param(self)
            logging.info('Executing: %s\n\tcmd_line: %s\n\tstdin: %s\n\tstdout: %s\n\tstderr: %s\n',
                         self.id, self.cmd_line, unicode(stdin), unicode(stdout), unicode(stderr))
            self.popen = Popen(self.args, stdin=stdin, stdout=stdout, stderr=stderr, cwd=self.cwd)
            if stdin == PIPE:
                time.sleep(.1)
                for line in self.stdin:
                    line = line + '\n' if not line.endswith('\n') else line
                    self.popen.stdin.write(line)
                    self.popen.stdin.flush()
        except Exception:
            self._close()
            raise
        return self.wait() if wait else self

    def wait(self):
        """ Wait for the process to finish and parse output if line parsers are supplied. """
        try:
            rlist = []
            if self.stdout.line_callback:
                rlist.append(self.stdout._r_handle)
            if self.stderr.line_callback:
                rlist.append(self.stderr._r_handle)
            if not rlist:
                self.popen.wait()
            else:
                select_args = rlist, [], [], .1
                done = False
                while not done:
                    if self.popen.poll() is not None:
                        done = True
                    ready = select.select(*select_args)[0]
                    if ready:
                        self.stdout._callback(ready)
                        self.stderr._callback(ready)
            level = logging.WARN if self.exit_code else logging.INFO
            message = 'Process finished with exit code %s: %s' % (self.exit_code, self.cmd_line)
            logging.log(level, message)
            if self.exit_code:
                raise SubprocessExecutionException(self, message)
        finally:
            self._close()
        return self

    def _close(self):
        self.stdout._close()
        self.stderr._close()
        if self.popen and isinstance(self.popen.stdin, file):
            self.popen.stdin.close()

    def kill(self):
        self._close()
        self.popen.kill()

    @property
    def cmd_line(self):
        """ Get the command line that can be used to rerun the process. """
        return ' '.join(map(print_prepare, self.args))

    @property
    def exit_code(self):
        """ Exit code returned by the process. None if process not finished. """
        return None if self.popen is None else self.popen.poll()

    @property
    def is_running(self):
        return self.popen is not None and self.exit_code is None

    def add_arg(self, *args, **kwargs):
        """ Append arguments to the argument list. For supplied kwargs, add_narg is called. """
        if self.popen is not None:
            raise Exception('Cannot add arguments once process has been executed.')
        for arg in args:
            if arg not in (None, ''):
                self.args.append(unicode(arg).strip())
        for key, val in kwargs.iteritems():
            self.add_narg(key, val)

    def add_narg(self, key, value):
        """ Add named arguments to the argument list. Examples:
        >>> p = Process('python')
        >>> p.add_narg('c', 'print 2*2') # Same as p.add_arg('-c', 'print 2*2')
        >>> p.add_narg('3', True) # Same as p.add_arg('-3'). For bool values, only key is added or nothing if False.
        """
        if value in (None, '') or value is False:
            return
        if not key.startswith('-'):
            key = '-' + key if len(key) == 1 else '--' + key
        if isinstance(value, bool):
            self.add_arg(key)
        else:
            self.add_arg(key, value)


def process_fails(exit_code, str_to_search=""):
    """ decorator for test functions that call Process.run() """
    def decorator(func):
        @functools.wraps(func)
        def wrapped():
            try:
                func()
                assert False, "SubprocessExecutionException expected, but not raised!"
            except SubprocessExecutionException as e:
                assert exit_code == e.proc.exit_code, 'Wrong exit code. expected: %s, actual: %s' % (exit_code, e.proc.exit_code)
                assert str_to_search in e.proc.stderr.get_string(), 'string "%s" was not found.' % str_to_search
        return wrapped
    return decorator
