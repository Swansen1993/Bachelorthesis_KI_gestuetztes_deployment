# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O XPath Mapping
# Source: app/utils/xpath.py

class Players:
    class Profile:
        ID = "//tm-subnavigation[@controller='spieler']//@id"
        URL = "//link[@rel='canonical']//@href"
        NAME = "//h1[@class='data-header__headline-wrapper']/descendant-or-self::*[not(self::span)]/text()"
        FULL_NAME = "//span[text()='Full name:']//following::span[1]//text()"
        DATE_OF_BIRTH_AGE = "//span[@itemprop='birthDate']//text()"
        CURRENT_CLUB_URL = "//span[@class='data-header__club']//a//@href"
        CURRENT_CLUB_NAME = "//span[@class='data-header__club']//text()"
        MARKET_VALUE = "//a[@class='data-header__market-value-wrapper']//text()"

    class Search:
        BASE = "//div[@class='box'][h2[contains(text(), 'players')]]"
        RESULTS = BASE + "//tbody//tr[@class='odd' or @class='even']"
        ID = ".//td[@class='hauptlink']//a/@href"
        NAME = ".//td[@class='hauptlink']//a//@title"