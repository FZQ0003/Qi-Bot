import os
import re
import shlex
import signal
import subprocess
import time
from pathlib import Path
from typing import IO

from .config import shell as config
from .logger import logger
from .time import get_str_time

TIMEOUT = config.timeout
SHELL_EXEC = config.shell_exec
CHECK_DIR = config.check_dir
REPLACE = config.output_replace


class CompletedProcess(object):
    code: int
    stdout: bytes
    stderr: bytes

    def __init__(self, code: int, stdout: bytes, stderr: bytes):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    @classmethod
    def from_subprocess(cls, process: subprocess.CompletedProcess):
        return cls(process.returncode, process.stdout, process.stderr)

    @staticmethod
    def bytes_decode(input_bytes: bytes) -> str:
        try:
            return input_bytes.decode()
        except UnicodeDecodeError:
            return '<BIN>'

    def as_string(self) -> str:
        output = '{}{}{}'.format(
            f'Return code: {self.code}\n',
            f'\nSTDOUT: \n{self.bytes_decode(self.stdout)}' if self.stdout else '',
            f'\nSTDERR: \n{self.bytes_decode(self.stderr)}' if self.stderr else ''
        )[:-1]
        for item in REPLACE.items():
            output = output.replace(item[0], item[1])
        return output

    def __str__(self) -> str:
        return self.as_string()


def _check(command: str) -> bool:
    # TODO: Checking.
    cmd_list = list(shlex.shlex(command, punctuation_chars=True))
    if '&' in cmd_list:
        logger.info('Command check failed: trying to hang up.')
        return False
    if not cmd_list:
        logger.info('Command check failed: no command passed.')
        return False
    return True


def cmd_analyze(command: str) -> str:
    """Analyze a command line."""
    if not _check(command):
        return ''
    return command


def _read_file(f: IO, tag: str) -> bytes:
    """Read IO not ended by EOF."""
    out_str = b''
    out_line = f.readline()
    tag = tag.encode()
    while tag not in out_line:
        out_str += out_line
        out_line = f.readline()
    return out_str


def single_cmd(command: str) -> CompletedProcess:
    """Run single command."""
    command = cmd_analyze(command)
    if not command:
        return CompletedProcess(132, b'', b'Command check failed!')
    try:
        return CompletedProcess.from_subprocess(subprocess.run(
            shlex.join(SHELL_EXEC + ['-c', command]),
            capture_output=True,
            shell=True,
            timeout=TIMEOUT
        ))
    except subprocess.TimeoutExpired as e:
        return CompletedProcess(137, e.stdout, e.stderr)


class Shell(object):
    """Define an interactive shell."""
    _name: str
    _enabled: bool = False
    _process: subprocess.Popen

    def __init__(self, name: str = None):
        self._name = name if name else get_str_time(False)

    def _check_point(self) -> str:
        """Generate check points for each command."""
        return f'{self._name}-{get_str_time(True)}'

    def _output(self, check_point: str = None) -> CompletedProcess:
        """Get output."""
        if not check_point:
            check_point = self._check_point()
        check_path = Path(CHECK_DIR, check_point)
        if check_path.is_file():
            return_code = int(check_path.read_text())
        else:
            return_code = None
            self._process.stdin.write(f'echo $? >/dev/stderr\n'.encode())
        self._process.stdin.write(
            f'echo {check_point} >/dev/stdout\n'
            f'echo {check_point} >/dev/stderr\n'.encode()
        )
        try:
            self._process.stdin.flush()
        except BrokenPipeError:
            logger.warning('Shell terminated.')
            self._enabled = False
            return CompletedProcess(-1, b'', b'')
        stdout = _read_file(self._process.stdout, check_point)
        stderr = _read_file(self._process.stderr, check_point)
        if return_code is None:
            err_list = stderr.split(b'\n')
            return_code = int(err_list[-2])
            stderr = b'\n'.join(err_list[:-2]) + b'\n'
        return CompletedProcess(return_code, stdout, stderr)

    def kill(self) -> None:
        """Kill all processes called by current shell."""
        for pid in subprocess.run(
                f'ps -o pid --ppid {self._process.pid} --no-headers',
                capture_output=True,
                shell=True,
        ).stdout.decode().split('\n')[:-1]:
            os.kill(int(pid), signal.SIGKILL)

    def start(self, env: dict = None) -> bool:
        """Start the shell."""
        if self._enabled:
            logger.warning('The current shell is still running.')
            return False
        self._process = subprocess.Popen(
            SHELL_EXEC,
            env=env if env else None,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        Path(CHECK_DIR).mkdir(mode=0o777, parents=True, exist_ok=True)
        if self._process.poll() is None:
            self._enabled = True
            return True
        logger.error('Failed to start shell!')
        return False

    def send(self, text: str) -> CompletedProcess:
        """Send command(s) to the shell."""
        timeout = TIMEOUT
        check_point = None
        for cmd_line in text.split('\n'):
            command = cmd_analyze(cmd_line)
            # Output never caught if simply called 'exit'
            if command == 'exit':
                return self.exit()
            command = re.sub('exit', 'Exit', command)
            check_point = self._check_point()
            check_path = Path(CHECK_DIR, check_point)
            self._process.stdin.write(
                f'{command}\n'
                f'echo $? >"{check_path}"\n'.encode()
            )
            self._process.stdin.flush()
            while timeout > 0 and not check_path.is_file():
                timeout -= 0.1
                time.sleep(0.1)
            if not timeout > 0:
                logger.warning('Reached timeout, kill the process.')
                self.kill()
                return self._output(check_point)
        if check_point is None:
            return CompletedProcess(2, b'', b'No command passed.')
        return self._output(check_point)

    def exit(self) -> CompletedProcess:
        """Gracefully close the shell."""
        if not self._enabled:
            logger.warning('The current shell is not running.')
            return CompletedProcess(2, b'', b'')
        try:
            stdout, stderr = self._process.communicate(
                f'touch "{CHECK_DIR}/{self._name}-exit"\n'
                f'rm "{CHECK_DIR}/{self._name}"*\n'
                'exit\n'.encode(),
                timeout=TIMEOUT
            )
        except subprocess.TimeoutExpired:
            self._process.terminate()
            stdout, stderr = '', 'Shell terminated.'
        if self._process.returncode != 0:
            logger.warning(f'Shell return code: {self._process.returncode}')
        self._enabled = False
        return CompletedProcess(self._process.returncode, stdout, stderr)

    @property
    def name(self) -> str:
        """The shell name."""
        return self._name

    @property
    def enabled(self) -> bool:
        """Check if the shell is running."""
        return self._enabled


if __name__ == '__main__':
    print('=== TEST START ===')
    print('[Test 1] Single command')
    while True:
        user_str = input('[Test 1] > ')
        if user_str == 'exit':
            break
        print(single_cmd(user_str))
    print('[Test 1] Exit.')
    print('[Test 2] Interactive shell')
    shell = Shell('FQi-Test')
    shell.start()
    while shell.enabled:
        user_str = input('[Test 2] > ')
        print(shell.send(user_str))
    print('[Test 2] Exit.')
    print('==== TEST END ====')
