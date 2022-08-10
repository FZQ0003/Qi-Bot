# Qi-Bot

> Creating directory...

## 计划开发的功能

* 文本转语音(TTS)
* 交互式终端
* 基于录播姬的B站开播提醒
* 图像处理相关
* 电路分析
* ...

## 部署

> 咕咕咕……  
> 有个`venv.sh`，可以先玩玩。

## 杂项

### 关于使用旧版Ariadne及相关模块的说明

坏了，全世界就我一只用0.6.x的了xwx

> Ref: [你急我也急](https://github.com/GraiaCommunity/Docs/commit/fc344902ddfb99813431b1a822ce1bb7f04ec164)

### 如何迁移至新版Ariadne

以如下环境为例：

```
graia-ariadne[graia] ~= 0.8.1
arclet-alconna[graia] ~= 1.1.2
```

修改`main.py`，将`OLD`内容替换为`NEW`内容：

OLD

``` python
import asyncio
...
from graia.ariadne.adapter import DefaultAdapter
...
from graia.ariadne.model import MiraiSession
from graia.broadcast import Broadcast
...
from graia.saya.builtins.broadcast import BroadcastBehaviour
...
bcc = Broadcast(loop=asyncio.new_event_loop())
app = Ariadne(
    connect_info=DefaultAdapter(
        broadcast=bcc,
        mirai_session=MiraiSession(
            host=bot.host,
            verify_key=bot.verify_key,
            account=bot.account
        ),
        log=False
    ),
    disable_logo=True,
    disable_telemetry=True
)
...
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
...
```

NEW

``` python
...
from graia.ariadne.entry import (
    config,
    HttpClientConfig,
    WebsocketClientConfig
)
...
app = Ariadne(
    config(
        bot.account,
        bot.verify_key,
        HttpClientConfig(host=bot.host),
        WebsocketClientConfig(host=bot.host)
    )
)
...
saya = Ariadne.create(Saya)
...
```

修改`Alconna`中`Args`的构造方法, 取消使用`slice`传入参数：

OLD

``` python
alc = Alconna(
    ...,
    main_args=Args['foo':int, 'bar':str:'default', ...]
)
```

NEW

``` python
alc = Alconna(
    ...,
    main_args=Args['foo', int]['bar', str, 'default'][...]
)
```

`AlconnaDispatcher`类初始化参数`alconna`改为`command`或直接去掉：

OLD

``` python
alc = Alconna(...)

@channel.use(ListenerSchema(
    ...,
    inline_dispatchers=[AlconnaDispatcher(alconna=alc)]
))
async def message(...):
    ...
```

NEW

``` python
alc = Alconna(...)

# Can hide param "command" -> AlconnaDispatcher(alc)
@channel.use(ListenerSchema(
    ...,
    inline_dispatchers=[AlconnaDispatcher(command=alc)]
))
async def message(...):
    ...
```


