import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcdbtItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CcdbtSpider(scrapy.Spider):
	name = 'cdbt'
	start_urls = ['https://www.cdbt.com/About-Us/Company/News']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('(//div[@class="Normal"])[1]/p/text()').get()
		try:
			date = re.findall(r'\w+\s\d+\,\s\d+', date)
		except TypeError:
			date = ""
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="Normal"]//text()[not (ancestor::div[@class="sidebarHIDE"] or ancestor::div[@class="container topFooterpadding"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcdbtItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
