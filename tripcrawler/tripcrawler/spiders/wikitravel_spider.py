from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from tripcrawler.items import HTMLDocumentItem


class WikitravelSpider(BaseSpider):
    name = "wikitravel"
    allowed_domains = ["wikitravel.org"]
#    start_urls = ["http://wikitravel.org/en/Europe"]
    start_urls = ["http://wikitravel.org/en/Amsterdam"]

    def parse(self, response):
        filename = "%s.html" % response.url.lower().split("/")[-1]
        open(filename, 'wb').write(response.body)

        hxs = HtmlXPathSelector(response)
        title = hxs.select('//title/text()').re('^\w+')[0]
        city = hxs.select('//body//h1/text()').extract()[0]
        country = hxs.select('//div[@id="contentSub"]//a[3]/text()').extract()[0]
        content = '\n'.join(filter(
                    lambda x: x and len(x) > 8,
                    hxs.select('//div[@id="bodyContent"]/p/text()').extract()))

        wtitem = HTMLDocumentItem()
        wtitem['title'] = title
        wtitem['city'] = city
        wtitem['country'] = country
        wtitem['content'] = content

        return [wtitem]

