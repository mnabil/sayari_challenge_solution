from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sos_search.spiders.cp_search_spider import CpSearchSpider
import os

path = os.path.dirname(os.path.abspath(__file__))

settings = get_project_settings()
settings.update({'FEED_URI': '{0}/data.json'.format(path)})

process = CrawlerProcess(settings)

process.crawl(CpSearchSpider, startswith='X', graph_output='graph_X.png')
process.start()