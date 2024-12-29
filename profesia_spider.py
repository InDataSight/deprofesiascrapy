import scrapy

class ProfesiaSpider(scrapy.Spider):
    name = 'profesia_spider'
    allowed_domains = ['profesia.sk']
    start_urls = ['https://www.profesia.sk/praca/?search_anywhere=data+engineer']
    #create urls set outside code - init dataset, incremental daily dataset
    #re-create output
    #create log
    #parellel process
    #document
    #crawl id and description
    #possible to crawl more?

    def parse(self, response):
        # Step 1: Detect <ul class="list">
        job_list = response.xpath('//ul[@class="list"]')
        if not job_list:
            self.logger.info('No job list found. Stopping spider.')
            return

        # Step 2: Detect all <li class="list-row">
        job_items = job_list.xpath('.//li[contains(@class, "list-row")]')
        if not job_items:
            self.logger.info('No job items found on this page.')
            return

        # Step 3: For each <li class="list-row">
        for job_item in job_items:
            # Step 4: Extract the offer ID from <h2><a>
            offer_link = job_item.xpath('.//h2/a')
            if offer_link:
                offer_id_attr = offer_link.attrib.get('id', '')
                if offer_id_attr.startswith('offer'):
                    offer_id = offer_id_attr.replace('offer', '')
                    self.logger.info(f'Found offer ID: {offer_id}')
                    # Step 5: Save the offer ID
                    yield {'offer_id': offer_id}
                else:
                    self.logger.warning('Offer ID not in expected format.')
            else:
                self.logger.warning('No offer link found in job item.')

        # Step 6: Navigate to the next page
        current_page = response.meta.get('page_num', 1)
        next_page_num = current_page + 1
        next_page_url = f'https://www.profesia.sk/praca/?search_anywhere=data+engineer&page_num={next_page_num}'

        # Attempt to retrieve the next page
        yield scrapy.Request(
            url=next_page_url,
            callback=self.parse,
            meta={'page_num': next_page_num},
            dont_filter=True
        )
