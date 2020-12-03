import re


def shorten_amazon_url(s):
    if any([i in s for i in ['.co.uk', '.com', '.de']]):
        short_link = ('https://smile.' + re.search('ama*zo*n.*?\/', s)[0] + re.search('\/(dp|gp/product)\/', s)[0][1:] + re.search('\/[a-zA-Z0-9]{10}\/?', s)[0][1:])
    else:
        short_link = ('https://www.' + re.search('ama*zo*n.*?\/', s)[0] + re.search('\/(dp|gp/product)\/', s)[0][1:] + re.search('\/[a-zA-Z0-9]{10}\/?', s)[0][1:])
    return short_link
