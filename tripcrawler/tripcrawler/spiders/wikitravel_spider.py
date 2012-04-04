from scrapy.spider import BaseSpider

class WikitravelSpider(BaseSpider):
    name = "wikitravel"
    allowed_domains = ["wikitravel.org"]
    start_urls = ["http://wikitravel.org/en/Europe"]

    def parse(self, response):
        filename = "%s.html" % response.url.split("/")[-1]
        open(filename, 'wb').write(response.body)
