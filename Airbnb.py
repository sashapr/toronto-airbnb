# -*- coding: utf-8 -*-
"""
Created: Sat Nov 1 20:29:41 2014
Modified: Apr-May 2018

Structure created: Hamel Husain
Modified: Sasha Prokosheva

AIRBNB page scraping
"""
from lxml import html
from bs4 import BeautifulSoup as soup
import re

# To manage connection to browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
# Save Chrome options for headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(executable_path=r"chromedriver.exe", chrome_options=chrome_options)

# For implementing random sleep
from random import randint
import time

# To save dictionary to csv
import unicodecsv as csv_unicode
import os
import csv


##############################################################################################
# Structure of links in AIRBNB, here it is used for a Canadian web (.ca)
# https://www.airbnb.ca/s/District--City--ST/homes  (ST = State or Province)
# Example: https://www.airbnb.ca/s/Thornhill--Vaughan--ON/homes
# For specific listings:
# http://www.airbnb.ca/rooms/listing_id (listing_id = integer ID of the specific listing)

base_url = 'https://www.airbnb.ca/s/'
base_url_listing = 'https://www.airbnb.ca/rooms/'
page_no_query = '/homes?'
page_no_query_plus = '/select_homes?'
page_query_string = '/homes?section_offset='
page_query_string_plus = '/select_homes?section_offset='
state = 'ON'

price_limit = 50000 # Absolute maximum price
##############################################################################################
# Details for saving to CSV
##############################################################################################
# File with individual IDs
csv_columns = ['city','district','page_number', 'listing_id', 'plus', 'price']
csv_columns_full = ['city','district', 'lat', 'long', 'listing_id', 'price', 'listing_type', 'title', 'num_bedrooms', 'num_beds', 'num_type_baths', 'num_guests', 'av_rating', 'num_host_reviews', 'num_reviews', 'joined']
csv_file_ids_01_10 = "csv/airbnb_toronto_ids_01_10.csv"
csv_file_full_01_10 = "csv/airbnb_toronto_full_01_10.csv"

##############################################################################################
# Results empty
##############################################################################################
results_empty = {    'listing_type': 'Not Found',
                     'title': 'Not Found',
                     'num_guests': 'Not Found',
                     'num_bedrooms': 'Not Found',  # zero if studio
                     'num_beds': 'Not Found',
                     'num_type_baths': 'Not Found',
                     'num_reviews': 'Not Found',
                     'av_rating': 'Not Found',
                     'long': 'Not Found',
                     'lat': 'Not Found',
                     'num_host_reviews': 'Not Found',
                     'joined': 'Not Found'
                     #'cancellation': 'Not Found'
                     }
##############################################################################################
##############################################################################################
def Locations(city):
    """
    input:
        city - name of the city
    output:
        districts - list of neighborhoods for a given city

    This function returns a sorted list of neighborhoods for a city, city.txt file with the column
    of district names should be in the directory "city" located in the same folder
    """
    file_name = 'city/' + city + '.txt'
    file = open(file_name, "r")
    districts = sorted([i for i in file])
    file.close()

    districts = [s.replace('\t', '') for s in districts]
    districts = [s.replace('\n', '') for s in districts]
    districts = [s.replace('\'', '-') for s in districts]
    districts = [s.replace('/', '-') for s in districts]
    districts = [s.replace(' ', '-') for s in districts]

    print('There are %s districts in total' % len(districts))
    return districts

##############################################################################################
# Outer function for getting all the listings: Iterate through pages
##############################################################################################
def IteratePage(city, distr = True, district_start = 1, district_finish = 1, loop_limit = 1):
    PageResults = []
    """
    input:
        city (string)           -  city, which will be transformed into districts string in Locations()
        district_start (int)    -  district to start scraping (in the ordered list of all districts)
        district_finish (int)   -  district to finish scraping (in the ordered list of all districts).
                                   If the number is larger than total in .txt file, it will be adjusted
                                   within the code.
        loop_limit (int)        -  maximum number of pages you want to parse. As of 2018,
                                   Airbnb shows only 300 pages of output for a specific location.
                                   To get listings for the whole big city like e.g. Toronto, it's required
                                   to slice it by districts, therefore use function Locations(city).

    output:
        list of dictionaries, with each list element corresponding to a unique listing

    This function iterates through the main listing pages where different properties
    are listed and there is a map, and collects the list of properties available along
    with the limited amount of information that is available in that page.  This function
    returns a list of dictionaries with each list element corresponding to a unique listing.
    Other functions will take the output from this function and iterate over them to explore
    the details of individual listings.
    """
    # Condition for district start
    if district_start <= 0:
        district_start = 1
    loc_state = '--' + state
    # Location strings, conditional on whether we consider city as the whole or split by districts
    if distr == True:
        location_list = Locations(city)
        loc_city = '--' + city
    else:
        location_list = ['Toronto']
        loc_city = ''
    print(len(location_list))
    loop_const = loop_limit

    # Conditions for district_start and district_finish
    if district_finish >= district_start:
        if district_finish > len(location_list):
            district_finish = len(location_list)
        number_districts = district_finish - district_start + 1

        for m in range(district_start-1, district_finish):
            location = location_list[m]
            #n = 1
            loop_limit = loop_const
            #price_min = 0
            try:
                print('Processing district %s %s out of %s to be processed' % (str(m+2-district_start), str(location), str(number_districts)))
                location_string = location + loc_city + loc_state
                # Identify pricing range for filtering
                price_min, price_max, pricing_string, total_pages = PricingRange(location_string)
                print(price_min, price_max, pricing_string, total_pages)

                while price_max <= price_limit:
                    loop_limit = total_pages

                    for n in range(1, loop_limit+1):
                        try:
                            print('Processing Page %s out of %s' % (str(n), str(loop_limit)))
                            if n == 1:
                                current_url = ''.join([base_url, location_string, page_no_query, pricing_string[1:]])
                            else:
                                current_url = ''.join([base_url, location_string, page_query_string, str(n-1), pricing_string])
                            PageSoup = ToSoup(current_url)
                            PageResults += ParsePageXML(PageSoup, city = city, district = location, url = current_url, page = str(n))

                        except:
                            print('This URL did not return results: %s ' % current_url)

                    # New value for minimum price
                    if price_max < price_limit:
                        price_min = price_max + 1
                        price_min, price_max, pricing_string, total_pages = PricingRange(location_string, price_min = price_min)
                    elif price_max == price_limit:
                        price_max += 1

                    print('Start processing pages for price limit from %s to %s' % (price_min, price_max))

            except:
                print('This district did not return results: %s ' % location)


        print('Done processing locations')
        return PageResults

    else:
        print('District to finish processing should be more or equal to district to start')
##############################################################################################
# Get bs4 page
##############################################################################################
def ToSoup(url = 'https://www.airbnb.ca/s/Thornhill--Vaughan--ON/homes'):
    '''
    input:  url
                this is the url for the type of listings you want to search.
                default is to use the generic url to search for listings
                in Thornhill, community in Vaughan, ON
    output: page_soup (bs4 page)
                error_links (list of links which did not return any results)

    This function tries several times to get scrape page. It gives up after 20 times and saves
    unsuccessful links.
    '''

    counter = 0
    listings = []
    details = []
    listing_missing = []
    error_links = []

    try:
        # Open connection and get data
        while len(listings) == 0 and counter !=100 and len(details) == 0 and len(listing_missing) == 0:
            counter += 1
            print('   Attempt to scrape page:', counter)
            time.sleep(randint(2,4))
            browser.get(url)
            # html parsing
            page_soup = soup(browser.page_source, 'html.parser')
            listings = page_soup.find_all('div', {'class' : '_v72lrv'})
            details = page_soup.find_all('div', {'class' : '_1kzvqab3'})
            listing_missing = page_soup.find_all('div', {'class' : '_1ibtygfe'})
            #print(len(listing_missing))

        if len(listing_missing) != 0:
            page_soup = []
        return page_soup

    except:
        print('Error Parsing Page - Skipping: %s' % url)
        error_links += url
        return page_soup

##############################################################################################
# Identify pricing range to filter
##############################################################################################
def PricingRange(location_string, price_min = 0, price_max = 50000, price_limit = 50000):
    '''
    This function identify which filter to apply for search in order to get all listings for
    districts with very large number of listings

    output: price_min, price_max, price_string, total_pages
    '''
    step = 100
    total_pages = 17
    # Pricing string to attach to URL
    pricing_string = '&price_min=' + str(price_min) + '&price_max=' + str(price_limit)

    try:
        current_url = ''.join([base_url, location_string, page_no_query, pricing_string[1:]])
        PageSoup = ToSoup(current_url)
        total_pages = int(PageSoup.find_all("div", {'class' : '_1bdke5s'})[-1].get_text())

        while total_pages >= 17:  # VERY IMPORTANT! Maximum number of pages Airbnb currently shows
            step = step // 2
            print('Decrease pricing range')
            price_max = price_min + step
            pricing_string = '&price_min=' + str(price_min) + '&price_max=' + str(price_max)
            current_url = ''.join([base_url, location_string, page_no_query, pricing_string[1:]])
            PageSoup = ToSoup(current_url)
            total_pages = int(PageSoup.find_all("div", {'class' : '_1bdke5s'})[-1].get_text())

        return price_min, price_max, pricing_string, total_pages

    except:
        print('Error making pricing strings')
        step = 1
        price_max = price_min + step
        pricing_string = '&price_min=' + str(price_min) + '&price_max=' + str(price_max)
        current_url = ''.join([base_url, location_string, page_no_query, pricing_string[1:]])
        PageSoup = ToSoup(current_url)
        total_pages = int(PageSoup.find_all("div", {'class' : '_1bdke5s'})[-1].get_text())
        return price_min, price_max, pricing_string, total_pages



##############################################################################################
# Get a dictionary of all listings for a corresponding area
##############################################################################################
def ParsePageXML(page_soup, city = 'Toronto', district = 'Deer-Park', url = '', page = 0):

    """
    input: page_soup
            parsed page
    input: city
            takes city from the IteratePage function
    input: district
            takes district from the IteratePage function

    output: dict
    ------
    This funciton parses one page with mulitple airbnb listings, and
    returns a list of dictionaries with IDs & whether it is a "plus" listing
    """
    p = 1
    ListingDB = []

    try:
        # get a list of containers for all posts at one page
        listings = page_soup.find_all('div', {'class' : '_v72lrv'})

        # add error handling
        for listing in listings:
            dat = {}
            # -> Listing ID
            tags = listing.find_all('a', {'class' : '_15ns6vh'})
            string = ''.join([tag.get('href') for tag in tags])
            dat['listing_id'] = re.search(r'\d+', string).group(0)

            # -> Plus
            tags = listing.find_all('div', {'class' : '_ncmdki'})
            string = ''.join([tag.get_text() for tag in tags])
            try:
                dat['plus'] = re.search(r'Plus', string).group(0)
            except:
                dat['plus'] = 'Regular'

            # -> Price
            tags = listing.find_all('div', {'class' : '_1yarz4r'})
            string = ''.join([tag.get_text() for tag in tags])
            dat['price'] = re.search(r'Price.*?per', string).group(0).replace('Price', '').replace('per', '')

            # Add page number and location information
            dat['city'] = city
            dat['district'] = district
            dat['page_number'] = page

            ListingDB.append(dat)
            p += 1
        print('   Scraped listings per page:', len(ListingDB))
        print(url)
        return ListingDB


    except:
        print('Error Parsing Page - Skipping: %s' % url)
        #if there is an error, just return an empty list
        return ListingDB

##############################################################################################
# Get attributes for every listing wrapper
##############################################################################################
def IterateListing(PageResults):
    """
    This function takes the list of dictionaries returned by the
    IteratePage (property IDs), and adds detailed data from the particular listing's infoself.
    If there is an error, the dictionary will be populated with default values of "Not Found"
    """
    FinalResults = []
    counter = 0

    for listing in PageResults:
        counter += 1
        print('Processing Listing %s out of %s' % (str(counter), str(len(PageResults))))

        #URL for a specific listing
        listing_url = ''.join([base_url_listing, str(listing['listing_id'])])
        # Get souped page
        print(listing_url)
        listing_soup = ToSoup(listing_url)
        # Get a ditionary with all details for a given listing ID
        DetailResults = Details(listing_soup, listing['listing_id'])

        #Collect Data
        CompleteListing = {**listing, **DetailResults}
        #Append To Final Results
        FinalResults.append(CompleteListing)

    return FinalResults

##############################################################################################
# Get attributes for every listing
##############################################################################################
def Details(html_parsed_soup, ListingID):
    '''
    input: html_parsed_soup (html parsed object)
    input: ListingID (integer)

    output: dict
    ------------
    This function takes a parsed page for the given listing ID as input and then returns
    a dictionary with values for this listing.
    '''

    Results = results_empty

    try:
        # -> Listing type
        Results['listing_type'] = GetListingType(html_parsed_soup)

        # -> Title
        Results['title'] = GetTitle(html_parsed_soup)

        # -> Possible number of guests, bedrooms, beds, number and type of bathrooms
        Results['num_guests'], Results['num_bedrooms'], Results['num_beds'], Results['num_type_baths'] = GetGuestsBeds(html_parsed_soup)

        # -> Number of reviews
        Results['num_reviews'] = GetNumReviews(html_parsed_soup)

        # -> Average rating
        Results['av_rating'] = GetAvRating(html_parsed_soup)

        # -> Latitude and Longitude
        Results['lat'], Results['long'] = GetLatLong(html_parsed_soup)

        # -> Number of host reviews
        Results['num_host_reviews'] = GetNumHostReviews(html_parsed_soup)

        # -> Owner joined
        Results['joined'] = GetJoined(html_parsed_soup)

        return Results

    except:
        # Just Return Initialized Dictionary
        return Results

##############################################################################################
# Functions to find objects on page
##############################################################################################
def GetListingType(html_parsed_soup):
    '''
    Listing type
    '''
    try:
        tags = html_parsed_soup.find_all('span', {'class' : '_bt56vz6'})
        if tags == []:
            tags = html_parsed_soup.find_all('span', {'class' : '_1k9f13qb'})
        string = ''.join([tag.get_text() for tag in tags])
        return string

    except:
        string = 'Not Found'
        return string

#############################################
def GetTitle(html_parsed_soup):
    '''
    Title
    '''
    try:
        tags = html_parsed_soup.find_all('h1', {'class' : '_1xu9tpch'})
        string = ''.join([tag.get_text() for tag in tags])
        return string

    except:
        string = 'Not Found'
        return string

#############################################
def GetGuestsBeds(html_parsed_soup):
    '''
    Possible number of guests, bedrooms, beds, number and type of bathrooms
    '''
    try:
        tags = html_parsed_soup.find_all('span', {'class' : '_y8ard79'})
        if tags == []:
            tags = html_parsed_soup.find_all('span', {'class' : '_8xnct4e'})

        string = ''.join([tag.get_text() for tag in tags])
        string = string[0:60]

        try:
            string = re.search(r'.*?bath', string).group(0)
        except:
            string = re.search(r'.*bed', string).group(0)

        try:
            studio = re.search(r'Studio', string).start()
        except:
            studio = 0

        try:
            half = re.search(r'[Hh]alf', string).start()
        except:
            half = 0

        if studio != 0 and half !=0:
            string = re.findall(r'\d+.*?\s.*?[^0-9]+', string)
            if len(string) == 5:
                string[3:5] = [''.join(string[3:5])]
                s4 = re.search(r'[A-Z].*', string[1]).group(0)
                s3 = string[1].replace(s4, '')
                s2 = re.search(r'[A-Z].*', string[0]).group(0)
                s1 = string[0]
            if len(string) == 3:
                s2 = re.search(r'[A-Z].*', string[0]).group(0)
                s1 = string[0].replace(s2, '')
                s3 = string[1]

        elif studio == 0 and half != 0:
            string = re.findall(r'\d+.*?\s.*?[^0-9]+', string)
            if len(string) ==5:
                string[3:5] = [''.join(string[3:5])]
                s4 = re.search(r'[A-Z].*', string[2]).group(0)
                s3 = string[2].replace(s4, '')
                s1 = string[0]
                s2 = string[1]
            if len(string) == 3:
                s4 = re.search(r'[A-Z].*', string[2]).group(0)
                s3 = string[2].replace(s4, '')
                s1 = string[0]
                s2 = string[1]

        elif studio != 0 and half == 0:
            string = re.findall(r'\d+.*?\s.*?[^0-9]+', string)
            if len(string) ==5:
                string[3:5] = [''.join(string[3:5])]
            s2 = re.search(r'[A-Z].*', string[0]).group(0)
            s1 = string[0].replace(s2, '')
            s3 = string[1]
            s4 = string[2]

        else:
            string = re.findall(r'\d+.*?\s.*?[^0-9]+', string)
            if len(string) == 5:
                string[3:5] = [''.join(string[3:5])]
                s1, s2, s3, s4 = string[0:4]
            if len(string) ==3:
                s1, s2, s3 = string[0:3]
                s4 = 'Not Found'
            if len(string) == 4:
                s1, s2, s3, s4 = string[0:4]

        return s1, s2, s3, s4

    except:
        s1 = 'Not Found'
        s2 = 'Not Found'
        s3 = 'Not Found'
        s4 = 'Not Found'
        return s1, s2, s3, s4

#############################################
def GetNumReviews(html_parsed_soup):
    '''
    Number of reviews
    '''
    try:
        tags = html_parsed_soup.find_all('div', {'class' : '_17erhr0e'})
        string = ''.join([tag.get_text() for tag in tags])
        string = re.search(r'.*?view', string).group(0)
        return string

    except:
        string = 'Not Found'
        return string

#############################################
def GetAvRating(html_parsed_soup):
    '''
    Averge Rating
    '''
    try:
        tags = str(html_parsed_soup.find_all('div', {'itemprop' : 'ratingValue'}))
        string = re.search(r'Rating.*?of\s5', tags).group(0)
        return string

    except:
        string = 'Not Found'
        return string

#############################################
def GetLatLong(html_parsed_soup):
    '''
    Latitude and Longitude
    '''
    try:
        tags = str(html_parsed_soup.find_all('div', {'id' : 'neighborhood'}))
        string = re.search(r'center=.*?\&', tags).group(0).replace('center=', '').replace('&', '')
        s1, s2 = string.split(',')
        return s1, s2

    except:
        s1 = 'Not Found'
        s2 = 'Not Found'
        return s1, s2

#############################################
def GetNumHostReviews(html_parsed_soup):
    '''
    Number of host reviews
    '''
    try:
        tags = html_parsed_soup.find_all('div', {'class' : '_36rlri'})
        string = ''.join([tag.get_text() for tag in tags])
        string = re.search(r'bath.*views', string).group(0).split('\U000f0004')[1]
        return string

    except:
        string = 'Not Found'
        return string

#############################################
def GetJoined(html_parsed_soup):
    '''
    Owner joined
    '''
    try:
        tags = str(html_parsed_soup.find_all('div', {'id' : 'host-profile'}))
        string = re.search(r'Joined.*?\d+', tags).group(0).replace('Joined in ', '').replace(' ','_')
        return string

    except:
        string = 'Not Found'
        return string
