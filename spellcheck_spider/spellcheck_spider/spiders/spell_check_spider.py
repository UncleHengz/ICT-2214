import scrapy
from textblob import TextBlob
from scrapy.crawler import CrawlerProcess
import logging

# # Disable all logging
logging.disable(logging.CRITICAL)

class SpellingGrammarCheckSpider(scrapy.Spider):
    name = 'spelling_grammar_check'

    def __init__(self, url=None, *args, **kwargs):
        super(SpellingGrammarCheckSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):
        text = ' '.join(response.xpath('//text()').extract())
        blob = TextBlob(text)

        custom_dictionary = {
    'assets','charset','ssl','src','href','instanceof','agentID','typeof','init','applicationID', 'ajax', 'api', 'html', 'css', 'javascript', 'json', 'xml', 'http', 'https', 'url', 'uri',
    'concat', 'const', 'var', 'let', 'function', 'async', 'await', 'promise', 'callback',
    'array', 'object', 'string', 'number', 'boolean', 'null', 'undefined', 'true', 'false',
    'for', 'while', 'do', 'if', 'else', 'switch', 'case', 'break', 'continue', 'return',
    'try', 'catch', 'finally', 'throw', 'new', 'class', 'extends', 'super', 'constructor',
    'prototype', 'this', 'bind', 'call', 'apply', 'map', 'filter', 'reduce', 'foreach',
    'queryselector', 'getelementbyid', 'innerhtml', 'textcontent', 'addeventlistener',
    'removeeventlistener', 'settimeout', 'setinterval', 'cleartimeout', 'clearinterval',
    'document', 'window', 'navigator', 'location', 'history', 'storage', 'localstorage',
    'sessionstorage', 'cookie', 'fetch', 'axios', 'xmlhttprequest', 'websocket', 'dom',
    'node', 'element', 'attribute', 'nodelist', 'fragment', 'shadowdom', 'template',
    'import', 'export', 'module', 'require', 'global', 'process', 'console', 'log',
    'debug', 'info', 'warn', 'error', 'assert', 'dir', 'dirxml', 'table', 'trace', 'group',
    'groupcollapsed', 'groupend', 'time', 'timeend', 'timeLog', 'count', 'countreset',
    'clear', 'status', 'statusText', 'headers', 'body', 'method', 'mode', 'credentials',
    'cache', 'redirect', 'referrer', 'referrerPolicy', 'integrity', 'keepalive', 'signal',
    'addEventListener', 'removeEventListener', 'dispatchEvent', 'initEvent', 'createEvent',
    'event', 'type', 'target', 'currentTarget', 'eventPhase', 'bubbles', 'cancelable',
    'defaultPrevented', 'composed', 'timeStamp', 'stopPropagation', 'stopImmediatePropagation',
    'preventDefault', 'initCustomEvent', 'detail', 'initUIEvent', 'view', 'which', 'initMouseEvent',
    'screenX', 'screenY', 'clientX', 'clientY', 'ctrlKey', 'shiftKey', 'altKey', 'metaKey',
    'button', 'buttons', 'relatedTarget', 'pageX', 'pageY', 'x', 'y', 'offsetX', 'offsetY',
    'movementX', 'movementY', 'getModifierState', 'initKeyboardEvent', 'key', 'code', 'location',
    'repeat', 'isComposing', 'getCoalescedEvents', 'getPredictedEvents', 'charCode', 'keyCode',
    'which', 'initFocusEvent', 'relatedTarget', 'initCompositionEvent', 'data', 'locale',
    'initMutationEvent', 'relatedNode', 'prevValue', 'newValue', 'attrName', 'attrChange',
    'initTransitionEvent', 'propertyName', 'elapsedTime', 'pseudoElement', 'initAnimationEvent',
    'animationName', 'elapsedTime', 'pseudoElement', 'initTouchEvent', 'touches', 'targetTouches',
    'changedTouches', 'altKey', 'metaKey', 'ctrlKey', 'shiftKey', 'rotation', 'scale'
}

        # Filter out correctly spelled words and words with non-alphabetic characters
        spelling_errors = [
            word for word in blob.words if word.isalpha() and not word.istitle() and word.lower() not in custom_dictionary and word.spellcheck()[0][1] < 0.95 and word.lower() != word.spellcheck()[0][0].lower()
        ]
        error_count = len(spelling_errors)

        print(f"Spelling Errors: {spelling_errors}")
        print(f"Number of Errors: {error_count}")

        if error_count > 200:  # Set your threshold for considering a website as a scam
            print(f"The website {response.url} is likely to be a scam website.")
        else:
            print(f"The website {response.url} is likely a legitimate website.")

if __name__ == "__main__":
    url = input("Enter the URL to check: ")
    process = CrawlerProcess()
    process.crawl(SpellingGrammarCheckSpider, url=url)
    process.start()