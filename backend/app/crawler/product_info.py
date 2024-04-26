import aiohttp
import asyncio
from lxml import etree
import re


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


def clean_text(text):
    # 移除制表符
    text = text.replace('\r', '')
    text = text.replace('\t', '')
    text = text.replace('纠错', '')
    text = text.replace('>', '')
    # 移除开头和结尾的空格
    text = text.strip()
    # 将连续的换行符替换为单个换行符
    text = re.sub(r'\s*\n\s*', '\n', text)
    return text


def parse(text, xpath):
    tree = etree.HTML(text)
    nodes = tree.xpath(xpath)
    all_texts = [''.join(node.xpath('.//text()')) for node in nodes]
    # 清理每个文本块
    all_texts = [clean_text(text) for text in all_texts if text.strip()]
    return all_texts


async def fetch_with_xpath(url, xpath):
    async with aiohttp.ClientSession() as session:
        text = await fetch(session, url)
        return parse(text, xpath)


# 使用示例
if __name__ == '__main__':
    async def main():
        url = 'https://detail.zol.com.cn/1611/1610863/param.shtml'
        xpath = '/html/body/div[10]/div[1]/div[1]/div[2]/table'
        texts = await fetch_with_xpath(url, xpath)
        with open('result1.txt', 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(text + '\n\n')


    # 运行异步主函数
    asyncio.run(main())
