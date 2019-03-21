import re
import requests
from urllib.parse import urlparse

# Removes all exact matches from a time-line according to the black list
class BlackList:
    
    def __init__(self, expressions):
        self.expressions = expressions
    
    def process(self, timeLine):
        results = []
        for j in range(len(timeLine)):
            segment = timeLine[j]['value']
            for k in range(len(self.expressions)):
                segment.discard(self.expressions[k])   
            if len(segment) != 0:
                results.append ({
                    'time': timeLine[j]['time'],
                    'value': segment
                })
        return results

# Takes all regular expression matches from a time-line according to the regular expressions white list
class RegularExpressionWhiteList:
    
    def __init__(self, expressions):
        self.expressions = expressions
    
    def process(self, timeLine):
        results = []
        for i in range(len(timeLine)):
            segments = []
            for segment in timeLine[i]['value']:
                for expression in self.expressions:
                    if None != re.match(expression, segment):
                        segments.append(segment)
            if len(segments):
                results.append ({
                    'time': timeLine[i]['time'],
                    'value': segments
                })
        return results

# Takes all Telegram hyperlinks
class TelegramHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        super().__init__(['https:\/\/t\.me\/'])

# Takes all Telegram group chat hyperlinks
class TelegramChatHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        super().__init__(['https:\/\/t\.me\/joinchat\/'])

# Takes all Telegram invitation hyperlinks
class TelegramInvitationHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        # Not a chat, not a sticker, not a robot
        super().__init__(['https:\/\/t\.me\/((?!joinchat|addstickers).(?![a-zA-Z0-9_]*\?start=).[a-zA-Z0-9_]*)'])
        
# Takes all Telegram bot hyperlinks
class TelegramBotHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        super().__init__(['https:\/\/t\.me\/([a-zA-Z0-9_]*)\?start='])

# Takes all Telegram invitation hyperlinks and removes additional parameters from them
class TelegramInvitationPureHyperlinks(TelegramInvitationHyperlinks):
    def process(self, timeLine):
        timeLine = super(TelegramInvitationPureHyperlinks, self).process(timeLine)
        results = []
        for i in range(len(timeLine)):
            segments = []
            for segment in timeLine[i]['value']:
                parsed = urlparse(segment)
                search = re.search('\/([a-zA-Z0-9_]*)', parsed.path)
                segment = parsed.scheme + '://' + parsed.netloc + '/' + search.group(1)
                segments.append(segment)
            if len(segments):
                results.append ({
                    'time': timeLine[i]['time'],
                    'value': segments
                })
        return results

class TelegramInvitationMetadata:

    def process(self, links):
        channels = []
        for uri in links:
            channel = {}
            channel["uri"] = uri
            file = requests.get(uri)
            text = file.text
            search = re.search('<div class="tgme_page_extra">([0-9 ]+)members', text)
            if None != search:
                channel["members"] = int(search.group(1).replace(' ', ''))
            else:
                channel["members"] = 0
            search = re.search('([0-9 ]+)online<\/div>', text)
            if None != search:
                channel["online"] = int(search.group(1).replace(' ', ''))
            else:
                channel["online"] = 0
            search = re.search('<div class="tgme_page_description">(.*?)<\/div>', text)
            if None != search:
                channel["description"] = search.group(1)
            else:
                channel["description"] = ''
            channels.append(channel)
        channels.sort(key=lambda x: x["members"], reverse=True)
        return channels
