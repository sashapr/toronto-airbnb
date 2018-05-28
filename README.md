## Description

I would like to understand Airbnb rental market in Toronto and how it is related to property prices. I describe assumptions and model in a more detailed [document](https://drive.google.com/open?id=1_KuIaytu1lvk99qkmY7KMDkgZK7leLmr). Here, I outline main steps and key outcomes of my project.


## Contents
I. Scraping data from Airbnb site <br/>
II. Cleaning data <br/>
III. Visualizations and analysis <br/>


## I. Scraping data from Airbnb site
Airbnb site links have the following structure:
- Page with listings for corresponding location: <span style="color:green">https://www.airbnb.ca/s/District--City--ST/homes</span>  (where ST = State or Province)
- Page with a specific listing: http://www.airbnb.ca/rooms/listing_id (where listing_id = integer ID)

Initial plan to get all the data:
1. Go through all pages with listings for every district in Toronto to get IDs
2. Go through every home individual page to get detailed information

Then I realized that Airbnb has a limit in showing number of pages per district. For example, https://www.airbnb.ca/s/Downtown-Toronto--Toronto/homes shows 300+ homes, but customer can browse only through first 17 pages (which is understandable, rarely we list through more pages and Airbnb can optimize its speed). To get all homes, I need to apply additional filter within function which will scrape pages for IDs. Thus, if a district has more than 300 homes, I add pricing filter. For example, one of the pages I scrape may look: https://www.airbnb.ca/s/Downtown-Toronto--Toronto/homes?price_min=40&price_max=62. Pricing step changes dynamically to optimize the speed of scraping. I start with average price and then decrease it by 2 in every iteration which returns more than 17 pages.

Additionally, while testing functions, I noticed that some listings may appear under different Districts. Therefore, I need additionally to get neighboorhood data by using latitude and longiture coordinates. I use geopy library to reverse scrape this information.

The updated scraping plan:
1. Go through all pages with listings for every district in Toronto to get IDs, apply pricing filter where needed
2. Go through every home individual page to get detailed information
3. Add neighborhood data based on latitude and longitude coordinates using geopy library



```markdown
Syntax highlighted code block


- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```
