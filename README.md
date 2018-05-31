## WORK IN PROGRESS
## Description

I would like to understand Airbnb rental market in Toronto and how it is related to property prices. I describe assumptions and model in a more detailed [document](https://drive.google.com/open?id=1_KuIaytu1lvk99qkmY7KMDkgZK7leLmr) (pdf). Here, I outline the main steps, challenges, and outcomes of my project.


## Contents
[I. Scraping data from Airbnb site](#i-scraping-data-from-airbnb-site) <br/>
[II. Cleaning data](#ii-cleaning-data) <br/>
[III. Graphs and analysis](#iii-graphs-and-analysis) <br/>


## I. Scraping data from Airbnb site
Canadian Airbnb site links have the following structure:
- Page with listings for corresponding location: <span style="color:MediumSeaGreen">`https://www.airbnb.ca/s/District--City--ST/homes`</span>  (where ST = State or Province, Districts = neighborhood within a City, for example Deerpark in city Toronto)
- Page with a specific listing: <span style="color:MediumSeaGreen">`http://www.airbnb.ca/rooms/listing_id`</span> (where listing_id = integer ID)

This was the initial plan to get the data:
1. Go through all pages with listings for every district in Toronto to get IDs
2. Go through every home individual page to get detailed information

Then I realized that Airbnb has a limit in showing number of pages per district. For example, <span style="color:MediumSeaGreen">`https://www.airbnb.ca/s/Downtown-Toronto--Toronto/homes`</span> shows 300+ homes, but customer can browse only through the first 17 pages (which is understandable, rarely we list through more pages and therefore Airbnb can optimize its speed). Thus, to get all listings, I need to apply additional filter within function which scrapes pages for IDs. I have chosen pricing filter. For example, one of the pages I scrape may look: <span style="color:MediumSeaGreen">`https://www.airbnb.ca/s/Downtown-Toronto--Toronto/homes?price_min=40&price_max=62`</span>. Pricing step changes dynamically to optimize the speed of scraping. I start with average price and then decrease it by 2 in every iteration which returns more than 17 pages.

Additionally, while testing functions, I noticed that some listings may appear under different Districts. Therefore, I need to get neighboorhood data by using latitude and longiture coordinates. I use [geopy](https://pypi.org/project/geopy) library to reverse scrape this information.

The updated scraping plan:
1. Go through all pages with listings for every district in Toronto to get IDs, apply pricing filter where needed
2. Go through every home individual page to get detailed information
3. Add neighborhood data based on latitude and longitude coordinates using geopy library



```
Code

![Image](src)
```

## II. Cleaning data

## III. Graphs and analysis


----------------------------------------------------
This is my first major project in Python. I used coding structure from a class project by [Hamel Hussein](https://github.com/hamelsmu) & his colleagues. They investigated Airbnb in Cambridge, MA with the objective to optimize the pricing for their listing. Functions were written in 2014 and as of now many libraries were outdated. Additionally, the structure of Airbnb pages changed, therefore I had to make numerous changes to the original code.
