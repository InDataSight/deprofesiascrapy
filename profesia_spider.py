"""
This module contains the ProfesiaSpider class for scraping job listings
from the Profesia website.
"""

import scrapy

class ProfesiaSpider(scrapy.Spider):
    """
    A Scrapy spider to scrape job listings from the Profesia website.
    """
    name = 'profesia_spider'
    allowed_domains = ['profesia.sk']
    start_urls = [
        'https://www.profesia.sk/praca/bratislavsky-kraj/plny-uvazok/'
        '?offer_agent_flags=8388&search_anywhere=data+engineer&skills[]=73__5_&sort_by=relevance'
    ]

    def parse(self, response):
        """
        Parse the response from the job listings page and extract job details.
        """
        job_list = response.xpath('//ul[@class="list"]')
        if not job_list:
            self.logger.info('No job list found. Stopping spider.')
            return

        job_items = job_list.xpath('.//li[contains(@class, "list-row")]')
        if not job_items:
            self.logger.info('No job items found on this page.')
            return

        for job_item in job_items:
            offer_data = self.extract_offer_data(job_item)
            self.logger.info(
                f'Found offer ID: {offer_data["offer_id"]}, Title: {offer_data["title"]}, '
                f'Employer: {offer_data["employer"]}, Money: {offer_data["money_text"]}, '
                f'Date: {offer_data["date_published"]}'
            )
            yield offer_data

        current_page = response.meta.get('page_num', 1)
        next_page_num = current_page + 1
        next_page_url = (
            'https://www.profesia.sk/praca/bratislavsky-kraj/plny-uvazok/'
            '?offer_agent_flags=8388&search_anywhere=data+engineer&skills[]=73__5_'
            f'&sort_by=relevance&page_num={next_page_num}'
        )

        yield scrapy.Request(
            url=next_page_url,
            callback=self.parse,
            meta={'page_num': next_page_num},
            dont_filter=True
        )

    def extract_offer_data(self, job_item):
        """
        Extract offer data from a job item.
        """
        offer_link = job_item.xpath('.//h2/a')
        offer_id = offer_link.attrib.get('id', '').replace('offer', '') if offer_link else None
        if not offer_id:
            self.logger.warning('Offer ID not found or in unexpected format.')

        title = offer_link.xpath('.//span[@class="title"]/text()').get() if offer_link else None
        if not title:
            self.logger.warning('Title not found.')

        employer = job_item.xpath('.//span[@class="employer"]/text()').get()
        if not employer:
            self.logger.warning('Employer not found.')

        money_text_before_svg = job_item.xpath(
            'normalize-space(.//span[@class="label-group"]//span[@class="label '
            'label-bordered green half-margin-on-top"]/text()[1])'
        ).get()
        money_text_after_svg = job_item.xpath(
            'normalize-space(.//span[@class="label-group"]//span[@class="label '
            'label-bordered green half-margin-on-top"]/text()[2])'
        ).get()
        money_text = f"{money_text_before_svg} {money_text_after_svg}".strip()
        if not money_text.strip():
            self.logger.warning('Money text not found.')

        date_published = job_item.xpath('.//span[@class="info"]/strong/text()').get()
        if not date_published:
            self.logger.warning('Date published not found.')

        return {
            'offer_id': offer_id,
            'title': title,
            'employer': employer,
            'money_text': money_text,
            'date_published': date_published
        }

# To run the spider and save the output with a timestamped filename:
# scrapy crawl profesia_spider -o offer_ids_$(date +%Y%m%d%H%M%S).json