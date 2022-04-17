# import asyncio
from typing import Union

from arclet.alconna import Alconna, Args, Option, Arpamar
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
# from graia.ariadne.message.element import At
from graia.ariadne.model import Group, Member
from graia.ariadne.util.async_exec import io_bound
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.shell import single_cmd, Shell  # , TIMEOUT, CompletedProcess

channel = Channel.current()

channel.name("Shell")
channel.description("Execute commands or start interactive shell.")
channel.author("F_Qilin")

command = Alconna(
    headers=['/'],
    command='sh',
    options=[
        Option('--command|-c', Args['*cmd': str]),
        Option('--env', Args['**args': str])
    ]
)
inc = InterruptControl(Saya.current().broadcast)


class InteractiveShellWaiter(Waiter.create([GroupMessage])):

    def __init__(self, group: Union[Group, int], member: Union[Member, int]):
        self.group = group if isinstance(group, int) else group.id
        self.member = member if isinstance(member, int) else member.id

    # noinspection PyMethodOverriding
    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if self.group == group.id and self.member == member.id:
            return message


@io_bound
def async_single_cmd(cmd: str):
    """Run single command."""
    return single_cmd(cmd)


class AsyncShell(object):
    """Define an interactive shell."""
    shell: Shell

    def __init__(self, name: str = None):
        self.shell = Shell(name)

    @io_bound
    def kill(self):
        """Kill all processes called by current shell."""
        return self.shell.kill()

    @io_bound
    def start(self, env: dict = None):
        """Start the shell."""
        return self.shell.start(env)

    @io_bound
    def send(self, text: str):
        """Send command(s) to the shell."""
        return self.shell.send(text)

    @io_bound
    def exit(self):
        """Gracefully close the shell."""
        return self.shell.exit()

    @property
    def name(self) -> str:
        """The shell name."""
        return self.shell.name

    @property
    def enabled(self) -> bool:
        """Check if the shell is running."""
        return self.shell.enabled


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[AlconnaDispatcher(alconna=command)]
))
async def shell_group_listener(app: Ariadne,
                               group: Group,
                               # member: Member,
                               message: MessageChain,
                               result: Arpamar):
    # env: dict = result.options.get('env', {}).get('args', None)
    cmd: tuple = result.options.get('command', {}).get('cmd', None)
    if cmd is None:
        await app.sendMessage(group, MessageChain(command.help_text), quote=message)
        # The interactive shell is disabled due to technical issues.
        # shell = AsyncShell(str(member.id))
        # await shell.start(env)
        # return_msg = MessageChain('===已建立交互式终端===')
        # last_quote = message
        # while shell.enabled:
        #     await app.sendMessage(group, return_msg, quote=last_quote)
        #     try:
        #         message: MessageChain = await inc.wait(
        #             InteractiveShellWaiter(group, member),
        #             timeout=TIMEOUT * 5
        #         )
        #     except asyncio.TimeoutError:
        #         await shell.exit()
        #         return_msg = MessageChain([At(member), '\n响应超时，终端已关闭。'])
        #         last_quote = False
        #     else:
        #         process: CompletedProcess = await shell.send(message.asDisplay())
        #         return_msg = MessageChain(process.as_string())
        #         last_quote = message
        # if last_quote:
        #     return_msg.append('\n终端已关闭。')
        # await app.sendMessage(group, return_msg, quote=last_quote)
    elif cmd:
        process = await async_single_cmd(' '.join(cmd))
        await app.sendMessage(group, MessageChain(process.as_string()), quote=message)
    else:
        await app.sendMessage(group, MessageChain('???'), quote=message)
