"""Scrapes Loudoun Wildlife Conservancy calendar through
February 2020, creates pandas dataframe of calendar information.
'https://loudounwildlife.org/events/'"""

from datetime import datetime as d
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
    event_dict['Event Venue Name'] = location(event)
    event_dict = lat_long(event_dict, event)
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
        fee_dict = {}
        fee_list = re.findall(r"[-+]?\d*\.\d+|\d+", event)
        fee_dict['Members'] = fee_list[0]
        fee_dict['Non-members'] = fee_list[1]
        if 'free for members' in event.lower():
            fee_dict['Members'] = '0'
            return fee_dict
        return fee_dict
    return str('None')

def month(url):
    soup = bs4_page(url)
    scripts = soup.find_all('script', {'type':'application/ld+json'})[1:]
    events = []
    for tag in scripts:
        event_list = json.loads(tag.string[2:])
        for event in event_list:
            event_dict = event_details(event)
            events.append(event_dict)
    return events

def location(event):
    if 'location' in event:
        if 'geo' in event['location']:
            return str(event['location']['name'])
    return str('None listed')

def lat_long(event_dict, event):
    if 'location' in event:
        
        return str(event['location']['geo']['latitude'])
    return str('None listed')

def lat_long(event_dict, event):
    if 'location' in event:
        if 'geo' in event['location']:
            event_dict['latitude'] = str(event['location']['geo']['latitude'])
            event_dict['longitude'] = str(event['location']['geo']['longitude'])
            return event_dict
    event_dict['latitude'] = 'None listed'
    event_dict['longitude'] = 'None listed'
    return event_dict

def clean(events):
    events.sort(key = lambda x: x['Event Start Date'])
    new_events = [i for n, i in enumerate(events) if i not in events[(n+1):]]
    return new_events

def main():
    events = month('https://loudounwildlife.org/events/')
    events += month('https://loudounwildlife.org/events/2020-02/')
    events = clean(events)
    return events