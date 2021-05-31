import time

import requests
from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from twilio.rest import Client


## Twilio Config, Optional if different notifier is used. 
TWILIO_PHONE_NUMBER = ''
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
SUBSCRIBER_PHONE_NUMBERS = ['']

## Zip code of the area you are looking for an Xbox. Needed for Target.
TARGET_ZIP_CODE = '30075'


class FindMeAnXboxX:

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=chrome_options)

    def run(self):
        while True:
            # self.walmart()
            self.gamestop()
            self.best_buy()
            self.target()
            time.sleep(3)
    
    def send_message(self, message):
        """This function can send the message anywhere. Twilio is what we chose in this script.
        Feel free to fork this repo and have it sent to a Slack channel or email for example.
        """
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        for number in SUBSCRIBER_PHONE_NUMBERS:
            client.messages.create(
                to=number, 
                from_=TWILIO_PHONE_NUMBER, 
                body=message)

    def notify_subscriber(self, url, extra_text=''):
        self.send_message("I found an Xbox Series X! %s %s" % (url, extra_text))

    def walmart(self):
        """Walmart seems to have robot detection, so consider modifying this function or don't look on walmart at all."""
        url = 'https://www.walmart.com/ip/Xbox-Series-X/443574645'
        self.driver.get(url)
        soup = Soup(self.driver.page_source, features='html.parser')
        section = soup.find('section', {'class': 'prod-PriceSection'})
        if section:
            price = section.find('span', {'class': 'visuallyhidden'}).text
            if price == '$499.99':
                status = soup.find('button', {'class': 'button spin-button prod-ProductCTA--primary button--primary'}).text
                if status == 'Add to cart':
                    self.notify_subscriber(url)

    def gamestop(self):
        url = 'https://www.gamestop.com/video-games/xbox-series-x/consoles/products/xbox-series-x/B224744V.html'
        self.driver.get(url)
        soup = Soup(self.driver.page_source, features='html.parser')
        status = soup.find('button', {'class': 'add-to-cart'}).text.strip()
        if status != 'Unavailable' and status != 'Not Available':
            self.notify_subscriber(url)

    def best_buy(self):
        url = 'https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p'
        self.driver.get(url)
        soup = Soup(self.driver.page_source, features='html.parser')
        status = soup.find('button', {'class': 'add-to-cart-button'}).text.strip()
        if status != 'Sold Out':
            self.notify_subscriber(url)

    def target(self):
        response = requests.get(
            url='https://api.target.com/fulfillment_aggregator/v1/fiats/80790841',
            params={
                'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01',
                'nearby': TARGET_ZIP_CODE,
                'limit': 200000,
                'requested_quantity': 1,
                'radius': 500
            }).json()
        url = 'https://www.target.com/p/xbox-series-x-console/-/A-80790841'
        out_of_stock_words = ['UNAVAILABLE', 'NOT_SOLD_IN_STORE', 'OUT_OF_STOCK']
        for location in response['products'][0]['locations']:
            if location.get('curbside') and location['curbside']['availability_status'] not in out_of_stock_words:
                status = location['curbside']['availability_status']
                self.notify_subscriber(url, '%s Curbside, %s' % (status, location['store_address']))
            if location.get('order_pickup') and location['order_pickup']['availability_status'] not in out_of_stock_words:
                status = location['order_pickup']['availability_status']
                self.notify_subscriber(url, '%s Order Pickup, %s' % (status, location['store_address']))
            if location.get('ship_to_store') and location['ship_to_store']['availability_status'] not in out_of_stock_words:
                status = location['ship_to_store']['availability_status']
                self.notify_subscriber(url, '%s Ship to Store, %s' % (status, location['store_address']))
            if location.get('in_store_only') and location['in_store_only']['availability_status'] not in out_of_stock_words:
                status = location['in_store_only']['availability_status']
                self.notify_subscriber(url, '%s In Store Only, %s' % (status, location['store_address']))


FindMeAnXboxX().run()
