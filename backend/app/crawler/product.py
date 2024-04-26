import aiohttp
import asyncio
from lxml import html

product_xpath = '//*[@id="J_PicMode"]/li'
count_xpath = '/html/body/div[4]/div[4]/div[1]/div[3]/span/b/text()'
page_xpath = "string(/html/body/div[4]/div[4]/div[1]/div[3]/div[1]/span[2])"


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_image(session, url):
    async with session.get(url) as response:
        return await response.read()


async def fetch_product_info(url):
    async with aiohttp.ClientSession() as session:
        try:
            page_content = await fetch(session, url)
            tree = html.fromstring(page_content)
            products = tree.xpath(product_xpath)

            product_list = []

            for product in products:
                product_data = {}
                # 检查列表是否为空，并设置默认值
                img_src_list = product.xpath('//li/a[@class="pic"]/img/@src')
                product_data['product_cover'] = img_src_list[0] if img_src_list else ''
                href_list = product.xpath('.//a[@class="pic"]/@href')
                product_data['href'] = href_list[0] if href_list else ''
                product_id_list = product.xpath('@data-follow-id')
                product_data['product_id'] = product_id_list[0] if product_id_list else ''
                product_data['product_rate'] = product.xpath('.//div[@class="comment-row"]/span[@class="score"]/text()')
                product_name_list = product.xpath('.//h3/a/text()')
                product_data['product_name'] = product_name_list[0] if product_name_list else ''
                hot_rank = product.xpath('.//div[@class="rank-row"]/a/span/text()')
                product_data['hot'] = hot_rank[0] if hot_rank else None
                product_list.append(product_data)
            return product_list

        except aiohttp.ClientError:
            return None


async def generate_url():
    async with aiohttp.ClientSession() as session:
        try:
            start_url = "https://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_2_0_1.html"
            page_content = await fetch(session, start_url)
            tree = html.fromstring(page_content)
            pages = tree.xpath(page_xpath)
            page_num = 0
            if len(pages) > 2:
                split_res = pages.split("/")
                page_num = int(split_res[1])
            url_list = []
            for i in range(page_num):
                url = f'https://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_2_0_{i + 1}.html'
                url_list.append(url)
            return url_list
        except Exception as e:
            print(e)
            return []

if __name__ == '__main__':
    async def main():
        # url = 'https://detail.zol.com.cn/cell_phone_index/subcate57_list_1.html'  # 替换为实际的URL
        # products_info = await fetch_product_info(url)
        # if products_info is not None:
        #     print(products_info)
        # else:
        #     print("Failed to fetch product information.")
        await generate_url()


    # 运行异步主函数
    # asyncio.run(main())
