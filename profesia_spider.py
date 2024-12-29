import scrapy
import datetime

class ProfesiaSpider(scrapy.Spider):
    name = 'profesia_spider'
    allowed_domains = ['profesia.sk']
    start_urls = ['https://www.profesia.sk/praca/bratislavsky-kraj/plny-uvazok/?count_days=31&offer_agent_flags=8388&search_anywhere=data+engineer&skills[]=73__5_&sort_by=relevance']

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
            # Steps 4: Extract the offer ID from <h2><a>
            offer_link = job_item.xpath('.//h2/a')
            offer_id = offer_link.attrib.get('id', '').replace('offer', '') if offer_link else None

            # Extract the title
            title = offer_link.xpath('.//span[@class="title"]/text()').get() if offer_link else None

            # Extract the employer
            employer = job_item.xpath('.//span[@class="employer"]/text()').get()

            # Extract the money text
            money_text = job_item.xpath('.//span[@class="label-group"]//span[@class="label label-bordered green half-margin-on-top"]/text()').get()

            # Extract the date published
            date_published = job_item.xpath('.//span[@class="info"]/strong/text()').get()

            # Log and yield the extracted data
            self.logger.info(f'Found offer ID: {offer_id}, Title: {title}, Employer: {employer}, Money: {money_text}, Date: {date_published}')
            yield {
                'offer_id': offer_id,
                'title': title,
                'employer': employer,
                'money_text': money_text,
                'date_published': date_published
            }

        # Step 6: Navigate to the next page
        current_page = response.meta.get('page_num', 1)
        next_page_num = current_page + 1
        next_page_url = f'https://www.profesia.sk/praca/bratislavsky-kraj/plny-uvazok/?count_days=31&offer_agent_flags=8388&search_anywhere=data+engineer&skills[]=73__5_&sort_by=relevance&page_num={next_page_num}'

        # Attempt to retrieve the next page
        yield scrapy.Request(
            url=next_page_url,
            callback=self.parse,
            meta={'page_num': next_page_num},
            dont_filter=True
        )

# To run the spider and save the output with a timestamped filename:
# scrapy crawl profesia_spider -o offer_ids_$(date +%Y%m%d%H%M%S).json