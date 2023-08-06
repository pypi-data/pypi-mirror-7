# Sqoot

## Acknowledgement
This python wrapper for sqoot takes inspiration from the foursquare wrapper created by Mike Lewis here: https://github.com/mLewisLogic/foursquare 

## Introduction
Python wrapper for the [sqoot v2 API](http://docs.sqoot.com/v2/overview.html).


Philosophy:

* Map Sqoot's endpoints one-to-one
* Clean, simple, Pythonic calls
* Only handle raw data, you define your own models

Features:

* Automatic retries
* Full endpoint coverage
* Full test coverage
* Useful exception classes
* Multi support (TODO:::In Progress)

Dependencies:

* requests

## Installation

    pip install sqoot

or

    easy_install sqoot

Depending upon your system and virtualenv settings, these may require sudo permissions.


## Usage

### Instantiating a client
    client = sqoot.Sqoot(privateApiKey='PRIVATE_API_KEY', publicApiKey='PUBLIC_API_KEY')

### Examples

#### [Categories](http://docs.sqoot.com/v2/categories.html)
##### Getting Categories
    client.categories()

#### [Clicks](http://docs.sqoot.com/v2/clicks.html)
##### Get clicks within a range of dates (defaults to the current month)
    client.clicks(params={'from':'2014-01-01T00:00:00Z', 'to':'2014-06-01T00:00:00Z', 'page':1})

#### [Coupons](http://docs.sqoot.com/v2/coupons.html)
##### Get the available coupons around a location
    client.coupons(params={"total": 1000, 
                           "page": 1, 
                           "per_page": 10, 
                           "query": "bagel", 
                           "online": 1, 
                           "location": {"address":     "444 Castro St.", 
                                        "locality":    "Mountain View",
                                        "region":      "CA",
                                        "postal_code": "94041",
                                        "country":     "United States",
                                        "latitude":    37.390751,
                                        "latitude":    37.390751,
                                        "longitude":   -122.080953
                                       }
                            "updated_after": "2013-11-04T16:18:04Z",
                            "order": "expires_at"
                           })

##### Get information about a specific coupon ID
    client.coupons.coupon(9722, params={})

##### Get the HTML code for the contents of the page for the coupon
    client.coupons.clickTrack(9722)

##### Get the image for the coupon (also used to track impressions)
    client.coupons.image(9722, params={'offer_id':9722, "geometry":"400x300"})

#### [Merchants](http://docs.sqoot.com/v2/merchants.html)
##### Get the details about a merchant, specifically what deals/coupons it offers
    client.merchants('761254', params={'id':'761254'})


### Full endpoint list
Note: endpoint methods map one-to-one with sqoot's endpoints

    categories()

    clicks()

    commissions()

    coupons()
    coupons.coupon()
    coupons.clickTrack()
    coupons.image()

    deals()
    deals.coupon()
    deals.clickTrack()
    deals.image()

    merchants()

    providers()

    multi()


### Testing
In order to run the tests:
* Copy `sqoot/tests/_creds.example.py` to `sqoot/tests/_creds.py`
* Fill in your personal credentials to run the tests (`_creds.py` is in .gitignore)
* Run `nosetests`


## Improvements
What else would you like this library to do? Let me know. Feel free to send pull requests for any improvements you make.

### TODO
* Bring in new endpoints as they emerge
* Test coverage for multi methods


## Code status
* TODO:::

## License
MIT License. See LICENSE
Copyright (c) 2014 Rajat Agarwal
