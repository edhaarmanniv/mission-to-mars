# Dependencies
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pymongo
import pandas as pd
import datetime as dt
from pprint import pprint


def make_soup(url):
    return BeautifulSoup(requests.get(url).text, "html.parser")


def scrape():
    """ scrapes associated sites to return a dictionary with results as key-value pairs
    """
    # NASA NEWS SCRAPE
    NASA_URL = "https://mars.nasa.gov/news/"
    nasa_soup = make_soup(NASA_URL)

    title_div = nasa_soup.body.find_all("div", class_="slide")[0]
    nasa_title = title_div.find_all("div", class_="content_title")[0].a.text.strip()
    nasa_desc = title_div.find("div", class_="rollover_description_inner").text.strip()

    # JPL FEATURED PHOTO
    JPL_IMAGE_URL_ROOT = "https://www.jpl.nasa.gov"
    JPL_IMAGE_URL = f"{JPL_IMAGE_URL_ROOT}/spaceimages/?search=&category=Mars"
    jpl_soup = make_soup(JPL_IMAGE_URL)

    image_container = jpl_soup.body.find_all("footer")[0].a
    large_file_path = (
        str(image_container["data-fancybox-href"])
        .replace("medium", "large")
        .replace("_ip", "_hires")
    )
    featured_image_url = f"{JPL_IMAGE_URL_ROOT}{large_file_path}"

    # MARS WEATHER FROM TWITTER
    WEATHER_TWITTER_URL = "https://twitter.com/marswxreport?lang=en"
    twitter_soup = make_soup(WEATHER_TWITTER_URL)

    tweet_text_container = twitter_soup.body.find_all(
        "p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"
    )
    mars_weather = ""
    for tweet in tweet_text_container:
        if tweet.text.startswith("InSight"):
            mars_weather = tweet.text[: tweet.text.find("pic.twitter.com")]
            break

    # MARS FACTS
    SPACE_FACTS_URL = "https://space-facts.com/mars/"
    space_soup = make_soup(SPACE_FACTS_URL)

    mars_table_container = space_soup.body.find_all(
        "table", id="tablepress-p-mars-no-2"
    )[0]

    mars_info_html = (
        pd.read_html(str(mars_table_container))[0]
        .rename(columns={0: "Description", 1: "Value"})
        .to_html(justify="left", index=False)
    )

    # MARS HEMISPHERES
    HEMISPHERES_URL_ROOT = "https://astrogeology.usgs.gov"
    HEMISPHERES_URL = (
        f"{HEMISPHERES_URL_ROOT}/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )
    hemi_soup = make_soup(HEMISPHERES_URL)

    hemisphere_image_urls = [
        {
            "title": soup.find_all("h2", class_="title")[0].text,
            "image_url": soup.find_all("a", target="_blank")[0]["href"],
        }
        for soup in [
            make_soup(url)
            for url in [
                f"{HEMISPHERES_URL_ROOT}" + a["href"]
                for a in hemi_soup.find_all("a", class_="itemLink product-item")
            ]
        ]
    ]

    return {
        "nasa_news": {"title": nasa_title, "desc": nasa_desc},
        "jpl_featured_image": featured_image_url,
        "weather_data": mars_weather,
        "mars_info": mars_info_html,
        "hemisphere_images": hemisphere_image_urls,
    }


if __name__ == "__main__":
    pprint(scrape())
