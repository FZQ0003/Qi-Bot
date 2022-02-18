from asyncio import sleep
from random import uniform

from graia.ariadne.message.chain import MessageChain

# Plain, Source, Quote, At, AtAll, Face
# Poke, Dice, MusicShare, Forward, File
# Image, FlashImage, Voice
# Xml, Json, App, MiraiCode
TIME_RESPONSE = 1
TIME_PER_LETTER = 0.2
TIME_RANDOM_FAC = 0.1
TIME_COPY = 3
TIME_FACTOR = {
    'Plain': None,  # 文本
    'Source': 0,  # 唯一标识
    'Quote': 0,  # 回复
    'At': 10,  # @
    'AtAll': 10,  # @全体成员
    'Face': 5,  # 表情
    'Poke': 2,  # 戳一戳
    'Dice': 10,  # 骰子
    'MusicShare': 15,  # 音乐分享
    'Forward': 20,  # 合并转发
    'File': 20,  # 文件
    'Image': 15,  # 图片
    'FlashImage': 18,  # 闪照
    'Voice': 10  # 语音
}


def random_fac(factor: float = TIME_RANDOM_FAC) -> float:
    return 1 + uniform(-factor, factor)


async def wait_for_typing(message: MessageChain):
    await sleep(TIME_RESPONSE)
    for element in message:
        factor = TIME_FACTOR.get(element.type, 0)
        if factor is None:
            factor = len(element.asDisplay().encode('utf-8'))
        await sleep(random_fac() * factor * TIME_PER_LETTER)


async def wait_for_copy():
    await sleep(random_fac() * (TIME_RESPONSE + TIME_COPY))
