# -*- coding: utf-8 -*-
"""
Created: May 2018

Created: Sasha Prokosheva

AIRBNB data cleaning
"""
# usual stuff
import numpy as np
import pandas as pd
import re

# geocoding
from geopy.geocoders import Nominatim
geolocator = Nominatim()

# For implementing random sleep
from random import randint
import time

# import functions from other files
from Airbnb import ToSoup, Details, IterateListing
from ReadWriteFunctions import *

##############################################################################################
# Different global constants
##############################################################################################
base_url_listing = 'https://www.airbnb.ca/rooms/'
csv_columns_full = ['city','district', 'lat', 'long', 'listing_id', 'price', 'listing_type', 'title', 'num_bedrooms', 'num_beds', 'num_type_baths', 'num_guests', 'av_rating', 'num_host_reviews', 'num_reviews', 'joined']

##############################################################################################
# Merge files, remove duplicates, split into a list of lists
##############################################################################################
def CleanIDs(pattern = 'csv/airbnb_toronto_ids*.csv', split_by = 1000):
    '''
    This functions imports files with IDs, removes duplicates and properties not in Toronto,
    then create a list of lists

    input: pattern  = files to merge
           split_by = how many entries per one list (this list will be then iterated to get
           individual details)
    output: list of data frames
    '''

    # Read files
    df = ReadCSVtoDF(pattern)
    # Drop PLUS listings
    try:
        df = df[df.plus != 'Plus']
    except:
        print('No plus column')
    # Delete redundant page and plus columns
    try:
        del df['plus']
        del df['page_number']
    except:
        print('Columns plus & page_number were already deleted')
    # Clean duplicates
    df = df.drop_duplicates()
    # Group districts in one field, separated by comma
    #if
    df = df.groupby('listing_id').agg({'city':'first', 'district': ', '.join, 'price':'first'}).reset_index()
    # Save all ids to CSVs
    SaveDFtoCSV('airbnb_toronto_ids_all', df)
    # make a list of data frames
    split = len(df) // split_by
    df_list = [df.iloc[i*split_by:(i+1)*split_by, :] for i in range(split)]
    df_list.append(df.iloc[split*split_by:, :])

    return df_list


##############################################################################################
# Cleaning wrapper
##############################################################################################
def Clean(pattern_full = 'csv/airbnb_toronto_full*.csv'):
    '''
    '''
    # Read files to a data frame
    df_full = ReadCSVtoDF(pattern_full)

    # Get rid of postings from other places
    df_full = df_full[(df_full['lat'].str.contains('42.|43.|44.') & ~df_full['lat'].str.contains('-')) | df_full['lat'].str.contains('Not Found')]

    df_full = df_full[(df_full['long'].str.contains('78.|79.|80.') & df_full['long'].str.contains('-')) | df_full['long'].str.contains('Not Found')]

    # Drop entries with all empty values -- properties that were taken off
    df_full = df_full[(df_full.num_bedrooms != 'Not Found') & (df_full.listing_type != 'Not Found') & (df_full.title != 'Not Found')]

    # Full database
    #df_full = df_full[['city', 'district', 'page_number', 'plus', 'lat', 'long', 'listing_id', 'price', 'listing_type', 'title', 'num_bedrooms', 'num_beds', 'num_type_baths', 'num_guests', 'av_rating', 'num_host_reviews', 'num_reviews', 'joined']]

    # ids which do not have full information
    ids = df_full.listing_id[(df_full["lat"] == "Not Found") & (df_full["num_bedrooms"] != "Not Found")].tolist()
    ids = list(set(ids))

    # Dictionary to iterate, to get missing values
    df = df_full[df_full.listing_id.isin(ids)]
    df = df[['city', 'district', 'page_number', 'listing_id', 'plus', 'price']].reset_index()
    del df['index']
    ResultsToUpdate = df.T.to_dict().values()

    # Drop items with these ids
    df_full = df_full[~df_full.listing_id.isin(ids)]
    # Delete redundant page and plus columns
    try:
        del df_full['plus']
        del df_full['page_number']
    except:
        print('Columns plus & page_number were already deleted')
    SaveDFtoCSV('airbnb_toronto_process_no_missing_info_ids', df_full)

    try:
        # Iterate over results with missing info, get results with info
        ResultsUpdated = IterateListing(ResultsToUpdate)
        csv_file_missing_values = "csv/airbnb_toronto_process_missing_values.csv"
        WriteDictToCSV(csv_file_missing_values, csv_columns_full, ResultsUpdated)

        return ResultsUpdated

    except:
        print("Error")
        return ResultsUpdated

##############################################################################################
# Merge data and clean variables wrapper
##############################################################################################
def MergeClean(pattern = 'csv/airbnb_toronto_process*.csv'):
    '''
    Function which merges data into one dataset and cleans variables/creates new
    '''
    # Read files into one data frame
    df = ReadCSVtoDF(pattern)

    #Drop values with no geo info, no info on type of property
    df = df[df.lat != 'Not Found']
    df = df[df.num_bedrooms != 'Not Found']
    df = df[df.num_type_baths != 'Not Found']

    # Delete redundant page and plus columns
    try:
        del df['plus']
        del df['page_number']
    except:
        print('Columns plus & page_number were already deleted')

    # Get rid of postings from other places
    df = df[(df['lat'].str.contains('42.|43.|44.') & ~df['lat'].str.contains('-')) | df['lat'].str.contains('Not Found')]

    df = df[(df['long'].str.contains('78.|79.|80.') & df['long'].str.contains('-')) | df['long'].str.contains('Not Found')]

    try:
        df = var_price(df)
    except:
        print('Error price cleaning')

    try:
        df = var_bedroom(df)
    except:
        print('Error bedroom cleaning')

    try:
        df = var_bed(df)
    except:
        print('Error bed cleaning')

    try:
        df = var_guest(df)
    except:
        print('Error guest cleaning')

    try:
        df = var_host(df)
    except:
        print('Error host reviews cleaning')

    try:
        df = var_review(df)
    except:
        print('Error reviews cleaning')

    try:
        df = var_share_type(df)
    except:
        print('Error type of share cleaning')

    try:
        df = var_bath(df)
    except:
        print('Error bath variables cleaning')

    try:
        df = joined(df)
    except:
        print('Error joined cleaning')

    # Delete redundant columns
    del df['num_type_baths']
    del df['joined']

    SaveDFtoCSV('airbnb_toronto_prefinal', df)

    return df
##############################################################################################
# Address
##############################################################################################
def GetAddress(pattern = 'csv/airbnb_toronto_prefinal*.csv', split_by = 500):
    '''
    This function goes through the list of lists of all addresses and retrieves district names
    from Google maps
    '''
    # Read file
    df = ReadCSVtoDF(pattern)

    # make a list of data frames
    split = len(df) // split_by
    df_list = [df.iloc[i*split_by:(i+1)*split_by, :] for i in range(split)]
    df_list.append(df.iloc[split*split_by:, :])

    # Add districts in a loop
    for split in range(len(df_list)):
        df = df_list[split]
        print('Processing batch %s' % split)
        try:
            df['neighbourhood'] = [Address(x, y) for (x, y) in zip(df['lat'], df['long'])]
            name = 'airbnb_toronto_with_neighborhoods' + str(split)
            SaveDFtoCSV(name, df)
        except:
            print('Error when processing %s part of list' % split)
    print('Done processing all')

##############################################################################################
# Functions to clean vars
##############################################################################################
def var_price(df):
    df.price = df.price.str.replace(' CAD', '').str.replace('$', '').str.replace(',', '')
    df.price = df.price.astype(int)
    return df

def var_bedroom(df):
    df.num_bedrooms = df.num_bedrooms.str.replace(' bedrooms', '').str.replace(' bedroom', '').str.replace('Studio', '0')
    df.num_bedrooms = df.num_bedrooms.astype(int)
    return df

def var_bed(df):

    df.num_beds = df.num_beds.str.replace(' beds', '').str.replace(' bed', '')
    df.num_beds = df.num_beds.astype(int)
    return df

def var_guest(df):
    df.num_guests = df.num_guests.str.replace(' guests', '').str.replace(' guest', '').str.replace('+', '')
    df.num_guests = df.num_guests.astype(int)
    return df

def var_host(df):
    df.num_host_reviews = df.num_host_reviews.str.replace(' Reviews', '').str.replace(' Review', '').str.replace('Not Found', '0')
    df.num_host_reviews = df.num_host_reviews.astype(int)
    return df

def var_review(df):
    df.num_reviews = df.num_reviews.str.replace(' Reviews', '').str.replace(' Review', '').str.replace('Not Found', '0')
    df.num_reviews = df.num_reviews.astype(int)
    return df

def var_share_type(df):
    df.listing_type = df.listing_type.str.replace('Room in aparthotel', 'Private room in aparthotel')
    df.listing_type = df.listing_type.str.replace('Room in boutique hotel', 'Private room in boutique hotel')
    df['share_type'] = [('shared room' if bool(re.search(r'^Shared', x)) == True else ('private room' if bool(re.search(r'^Private', x)) == True else 'entire property')) for x in df.listing_type]
    df['home_type'] = pd.np.where(df.listing_type.str.contains('apartment'), 'apartment',
                   pd.np.where(df.listing_type.str.contains(' house'), 'house',
                   pd.np.where(df.listing_type.str.contains('condo'), 'condo',
                   pd.np.where(df.listing_type.str.contains('guest suit'), 'guest suit',
                   pd.np.where(df.listing_type.str.contains('townhouse'), 'townhouse',
                   pd.np.where(df.listing_type.str.contains('bungalow'), 'bungalow',
                   pd.np.where(df.listing_type.str.contains('bed and breakfast'), 'b&b',
                   pd.np.where(df.listing_type.str.contains('loft'), 'loft',
                   pd.np.where(df.listing_type.str.contains('guesthouse'), 'guesthouse',
                   'other')))))))))
    return df

def var_bath(df):
    df.num_type_baths = [(x + '5 bath' if len(x) == 2 else ('0.5 bath' if bool(re.search(r'[Hh]alf-bath', x)) == True else x)) for x in df.num_type_baths]
    df['num_baths'] = df.num_type_baths.str.replace(' bath', '').str.replace(' shared', '').str.replace(' private', '').str.replace('Not Found', '').str.replace('Shared', '').str.replace('Private', '')
    df['type_baths'] = [('shared' if bool(re.search(r'.*[Ss]hared', x)) == True else ('private' if bool(re.search(r'.*[Pp]rivate', x)) == True else 'unknown')) for x in df.num_type_baths]
    return df

def joined(df):
    df['joined_month'], df['joined_year'] = df.joined.str.split('_', 1).str
    return df

##############################################################################################
# Return address dictionary by lat and long
##############################################################################################
def Address(lat, long):
    '''
    This function returns address by geo coordinates for columns with latitude ('lat') and longitude ('long')
    '''
    address = {}
    counter = 0
    location_string = lat + ', ' + long

    while len(address) == 0 and counter != 50:
        counter += 1
        #print('   Attempt to get location:', counter)
        time.sleep(randint(0,2))
        try:
            location = geolocator.reverse(location_string)
            address = location.raw['address']
        except:
            address = {}
        print(counter)

    try:
        neighbourhood = address['neighbourhood']
    except:
        neighbourhood = []

    print('Processed address')
    return neighbourhood
