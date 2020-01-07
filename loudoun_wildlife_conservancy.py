"""Scrapes Loudoun Wildlife Conservancy calendar through
February 2020, creates pandas dataframe of calendar information.
'https://loudounwildlife.org/events/"""

from datetime import datetime, timedelta
import json
import logging
import re

import bs4
import requests

logger = logging.getLogger(__name__)

def soupify_page(url = 'https://loudounwildlife.org/events/'):
    try:
        r = requests.get(url)
    except Exception as e:
        logger.critical(f'Exception making GET to {url}: {e}', exc_info=True)
        return
    content = r.content
    soup = bs4.BeautifulSoup(content, 'html.parser')
    
    return soup
