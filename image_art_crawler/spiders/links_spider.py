import scrapy
import re
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from image_art_crawler.items import ImageArtCrawlerItem


keys_map={u'G\xe9nero': 'genre', u'Autor': 'author', u'Origen': 'origin', u'Medidas': 'dimmensions', u'Objeto': 'object', 
    u'Estilo': 'style', u'T\xe9cnica': 'technique', u'Soporte': 'support', u'Escuela': 'school', u'Fecha':'date'}

class LinkArtSpider(CrawlSpider):
    name = "linkArt"

    def start_requests(self):
        queries =['antonio+berni','pridiliano+pueyrredon', 'emilio+pettoruti', 'lino+spilimbergo']
        urls = [
            'https://www.bellasartes.gob.ar/coleccion/buscar?q='
        ]
        for url in urls:
            for q in queries:
                yield scrapy.Request(url=url+q, callback=self.parse)


    def parse(self, response):
        for link in LxmlLinkExtractor(allow=r'https://www.bellasartes.gob.ar/coleccion/obra/.+', restrict_xpaths='//div[@class="obra card"]').extract_links(response):
            yield response.follow(link, self.parse_image)
        

    def parse_image(self, response):
        data_image = {}
        data_image['name'] = response.css('#data h1::text').extract_first()
        data_image['id'] = response.css('div.numinv span::text').extract_first()

        for data in response.css('#data li '):
            values = data.css('::text').re(r'[^\n\t]+')
            if (len(values) != 0) and (re.sub(r'[: ]+', '', values[0]) in keys_map.keys()):
                key = keys_map[re.sub(r'[: ]+', '', values[0])]
                data_image[key] = ' '.join(values[1:])
        #print(data_image)
        relative_image_url = response.css('#image a.hd.non-printable::attr(href)').extract_first()
        image_url = response.urljoin(relative_image_url)
        yield ImageArtCrawlerItem(id= data_image['id'], name=data_image['name'], data=data_image, image_urls=[image_url])  
#        print(response.css('div.buttons.non-printable a.btn.next ::attr(href)').extract())
        


