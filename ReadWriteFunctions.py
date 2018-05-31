# -*- coding: utf-8 -*-
"""
Created on: May 2018

Created by: Sasha Prokosheva

Functions to read and write different types of data to/from CSV
"""
# usual stuff
import numpy as np
import pandas as pd
import re

# To save dictionary to csv
import unicodecsv as csv_unicode
import os
import csv

# To read several files
import glob

##############################################################################################
# Details for saving to CSV
##############################################################################################
# File with individual IDs
csv_columns = ['city','district','page_number', 'listing_id', 'plus', 'price']
csv_columns_full = ['city','district', 'lat', 'long', 'page_number', 'listing_id', 'plus', 'price', 'listing_type', 'title', 'num_bedrooms', 'num_beds', 'num_type_baths', 'num_guests', 'av_rating', 'num_host_reviews', 'num_reviews', 'joined']
csv_file_ids_01_10 = "csv/airbnb_toronto_ids_01_10.csv"
csv_file_full_01_10 = "csv/airbnb_toronto_full_01_10.csv"




##############################################################################################
# Save Results to CSV
##############################################################################################
def WriteDictToCSV(csv_file, csv_columns, dict_data):
    '''
    csv_file: full path to the file
    csv_columns: list with column names
    dict_data: list of dictionaries
    '''
    try:
        with open(csv_file, 'wb') as csvfile:
            writer = csv_unicode.DictWriter(csvfile, fieldnames=csv_columns, lineterminator='\n', encoding='utf-8')
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except:
        print("Error")

##############################################################################################
# Read Results from CSV to dictionary
##############################################################################################
def ReadDictFromCSV(csv_file):
    '''
    csv_file: full path to the file
    '''
    try:
        with open(csv_file, 'r') as file:
            dict = [{k: v for k, v in row.items()} for row in csv.DictReader(file, skipinitialspace=True)]
        return dict

    except:
        print("Error")

##############################################################################################
# Function to read CSV files in the directory and create one data frame
##############################################################################################
def ReadCSVtoDF(pattern = 'csv/airbnb_toronto_full*.csv'):
    '''
    input (string)
    output (pandas df)
    ----------------------------
    This function takes a pattern (path to CSVs) and reads files into pandas data frame
    '''
    try:
        csv_files = glob.glob(pattern)
        dfs = []
        for file in csv_files:
            frame = pd.read_csv(file, dtype=object)
            dfs.append(frame)
        df = pd.concat(dfs)

        return df

    except:
        print('Error in reading')

##############################################################################################
# Function to save DF to a CSV
##############################################################################################
def SaveDFtoCSV(csv, DataFrame):
    '''
    Saves df into a CSV file. CSV = file name, it will be saved into a directory 'csv'
    located in working directory
    '''
    path = 'csv/' + csv + '.csv'
    try:
        DataFrame.to_csv(path, index=False, encoding='utf-8')

    except:
        print("Error")
