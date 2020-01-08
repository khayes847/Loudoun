"""Scrapes Loudoun Wildlife Conservancy calendar through
February 2020, creates pandas dataframe of calendar information.
'https://loudounwildlife.org/events/'"""

from datetime import datetime, timedelta
import json
import logging
import re

import bs4
import requests

logger = logging.getLogger(__name__)

def bs4_page(url):
    try:
        r = requests.get(url)
    except Exception as e:
        logger.critical(f'Exception making GET to {url}: {e}', exc_info=True)
        return
    content = r.content
    soup = bs4.BeautifulSoup(content, 'html.parser')
    return soup
            
def event_details(event):
    event_dict = {}
    event_dict['Event Name'] = event['name']
    event_dict['Event Description'] = event_description(event['url'])
    event_dict['Event Start Date'] = event['startDate'][:10]
    event_dict['Event Start Time'] = event['startDate'][11:19]
    event_dict['Event End Date'] = event['endDate'][:10]
    event_dict['Event End Time'] = event['endDate'][11:19]
    event_dict['All Day Event'] = False
    event_dict['Timezone'] = 'America/New_York'
    event_dict['Event Venue Name'] = event['location']['name']
    event_dict['Event Organizers'] = 'Loudoun Wildlife Conservancy'
    event_dict['Event Cost'] = fees(event_dict['Event Description'])
    event_dict['Event Currency Symbol'] = '$'
    event_dict['Event Category'] = ''
    event_dict['Event Website'] = event['url']
    event_dict['Event Featured Image'] = event['image']
    return event_dict

def event_description(url):
    soup = bs4_page(url)
    script = soup.find('div',
                       {'class':
                        "tribe-events-single-event-description tribe-events-content"})
    desc = script.text
    desc = re.sub(r"\n",'', desc)
    desc = re.sub(r"\xa0",'', desc)
    desc = re.sub(r"Share via:More",'', desc)
    return desc

def fees(event):
    if 'Fee:' in event:
        fee_list = re.findall(r"[-+]?\d*\.\d+|\d+", event)
        return fee_list
    return []

def main():
    soup = bs4_page('https://loudounwildlife.org/events/')
    scripts = soup.find_all('script', {'type':'application/ld+json'})[1:]
    events = []
    for tag in scripts:
        event_list = json.loads(tag.string[2:])
        for event in event_list:
            event_dict = event_details(event)
            events.append(event_dict)
    return events