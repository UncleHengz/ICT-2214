import scrapy
from scrapy.crawler import CrawlerProcess
from google.cloud import language_v1

class GoogleLanguageCheckSpider(scrapy.Spider):
    name = 'google_language_check'

    def __init__(self, url=None, *args, **kwargs):
        super(GoogleLanguageCheckSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):
        text = ' '.join(response.xpath('//text()').extract())
        client = language_v1.LanguageServiceClient()

        # Check for syntax errors in the text
        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        syntax = client.analyze_syntax(document=document)

        # Count the number of spelling and grammatical errors
        error_count = sum(token.part_of_speech.tag == language_v1.PartOfSpeech.Tag.AFFIX for token in syntax.tokens)

        if error_count > 10:
            print(f'The website {response.url} may be a scam website. Detected {error_count} spelling/grammatical errors.')
        else:
            print(f'The website {response.url} is likely a legitimate website. Detected {error_count} spelling/grammatical errors.')

if __name__ == "__main__":
    url = input("Enter the URL to check: ")
    process = CrawlerProcess()
    process.crawl(GoogleLanguageCheckSpider, url=url)
    process.start()
