from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

class PisosScraper:

    def scrape_data(self, url):

        data_from_web_dictionary = {
            "Baños: ": "bathrooms",
            "Aire acondicionado: ": "hasAirConditioning" ,
            "Terraza: ": "hasTerrace" ,
            "Terraza": "hasTerrace" ,
            "Jardín: ": "hasGarden",
            "Piscina: ": "hasSwimmingPool",
            "Ascensor": "hasLift",
            "Garaje: ": "hasGarage",
            "Garaje": "hasGarage",
            "Calefacción: ": "hasCentralHeating",
            "Trastero": "hasStorage",
            "armarios empotrados": "hasFittedWardrobes",
            "Lujo": "isLuxury",
            "Primera línea de playa": "hasSeaView",
            "Vistas al mar": "hasSeaView",
            "Planta: ": "floor",
            "Orientación: ": "orientations",
            "Habitaciones: ": "rooms",
            "Superficie construida: ": "size",
            "Superficie útil: ": "usableSize",
            "Superficie solar: ": "plotSize"
        }

        base_url = url.split(".com/")[0] + '.com/'

        properties = []
        last_page = 100

        def get_numbers(value):
            numbers_str = ""
            allowed_chars = "1234567890"
            for char in value:
                if char in allowed_chars:
                    numbers_str = numbers_str + char
            
            if len(numbers_str) > 0:
                return int(numbers_str)
            else: 
                return (0)

        for i in range(last_page) :
            page = i + 1
            html_page = requests.get(url + str(page))
            elements_page = BeautifulSoup(html_page.text, 'html.parser').find_all("div", {"class": "ad-preview"})

            for element in elements_page:
                script_tag = element.find("script").text
                script_tag_json = json.loads(script_tag)

                property = {
                    'id': script_tag_json["@id"],
                    'url': script_tag_json["url"],
                    'latitude': script_tag_json['geo']["latitude"],
                    'longitude': script_tag_json['geo']['longitude']
                }

                properties.append(property)

        values = []
        labels = []
        values_dictionary = []
        labels_dictionary = []
        features_dictionary = {}

        for property in properties:
            property_page_html = requests.get(base_url + property['url'])
            soup_property_html_page = BeautifulSoup(property_page_html.text, 'html.parser')
            elements_content = soup_property_html_page.find_all("div", {"class": "features__content"})
            elements_label = soup_property_html_page.find_all("div", {"class": "features__label"})
            id = property['id']

            tag_element = soup_property_html_page.find("div", {"class": "mediaTag__tag"})
            tag = ''
            if tag_element:
                tag = tag_element.text

            features_dictionary[id] = {
                "id": id,
                "address": '',
                "bathrooms": 0,
                "title": "",
                "contactInfo": {
                    "contactName": "",
                    "userType": "professional",
                    "agencyLogo": None,
                    "commercialName": None,
                    "phone": None
                },
                "country": "es",
                "dataSource": "pisos",
                "description": '',
                "detailedType": {
                    "subTypology": "",
                    "typology": "",
                    "isVilla": False
                },
                "district": "",
                "externalReference": "",
                "features": {
                    "hasAirConditioning": False,
                    "hasTerrace": False,
                    "hasGarden": False,
                    "hasSwimmingPool": False,
                    "hasLift": False,
                    "hasGarage": False,
                    "hasSeaView": False,
                    "hasCentralHeating": False,
                    "hasStorage": False,
                    "hasFittedWardrobes": False,
                    "hasBalcony": False,
                    "hasGreenery": False,
                    "isLuxury": False
                },
                "latitude": property["latitude"],
                "longitude": property["longitude"],
                "multimedia": {
                    "images": [],
                    "videos": [],
                    "plans": [],
                    "virtualTour": None
                },
                "municipality": "",
                "neighborhood": "",
                "price": '',
                "priceDropValue": 0,
                "propertyCode": "",
                "province": "",
                "rooms": 0,
                "size": 0,
                "usableSize": None,
                "plotSize": None,
                "status": "",
                "thumbnail": "",
                "url": property["url"],
                "initialImportTime": 0,
                "floor": None,
                "numFloors": None,
                "yearConstructed": None,
                "energyCertificate": {
                    "inProgress": False,
                    "consumptionGrade": None,
                    "emissionGrade": None
                },
                "orientations": [],
                "parentDuplicateId": '',
                "priceHistory": [],
                "listingHistory": [],
                "buildingType": "property",
                "isBankProperty": False
            }

            price_element = soup_property_html_page.find("div", {"class": "price__value"})
            if price_element:
                features_dictionary[id]['price'] = get_numbers(price_element.text)
            
            address_element = soup_property_html_page.find("span", {"id": "selectedZone"})
            if address_element:
                features_dictionary[id]['address'] = address_element.text
            
            description_element = soup_property_html_page.find("div", {"class": "description__content"})
            if description_element:
                features_dictionary[id]['description'] = description_element.text

            contact_info_element = soup_property_html_page.find("div", {"class": "js-contactInfo"})
            if contact_info_element:
                features_dictionary[id]['parentDuplicateId'] = soup_property_html_page.find("div", {"class": "js-contactInfo"}).get('data-new-development-parent-id')

            drop_price_element = soup_property_html_page.find("div", {"class": "jsPriceDropValue"})
            if drop_price_element:
                drop_price_str = drop_price_element.text.split()[0]
                features_dictionary[id]["dropPriceValue"] = get_numbers(drop_price_str)

            address_splitted = features_dictionary[id]['address'].split(", ")
            features_dictionary[id]["district"] = address_splitted[0]
            if len(address_splitted) > 1:
                features_dictionary[id]["municipality"] = address_splitted[1]

            elements_details_block = soup_property_html_page.find_all("div", {"class": "details__block"})
            for element in elements_details_block:
                soup_title = element.find('h1')
                if soup_title:
                    title = soup_title.text
                    features_dictionary[id]["title"] = title
                    features_dictionary[id]['detailedType']['typology'] = title.split()[0]

            owner_name_element = soup_property_html_page.find("p", {"class": "owner-info__name"})
            if owner_name_element:
                features_dictionary[id]["contactInfo"]['contactName'] = owner_name_element.text
                features_dictionary[id]["contactInfo"]['commercialName'] = owner_name_element.text
            
            onwer_phone_element = soup_property_html_page.find("div", {"class": "owner-info__phone"})
            if onwer_phone_element:
                features_dictionary[id]["contactInfo"]['phone'] = onwer_phone_element.find('span').text

            element_logo = soup_property_html_page.find("img", {"class": "owner-info__logo"})
            if element_logo:
                logo = element_logo.get("src")
                features_dictionary[id]["contactInfo"]['agencyLogo'] = logo
            
            energy_certificate_tags = soup_property_html_page.find_all("span", {"class": "energy-certificate__tag"})
            if len(energy_certificate_tags) > 0:
                features_dictionary[id]["energyCertificate"]['consumptionGrade'] = energy_certificate_tags[0].text
                features_dictionary[id]["energyCertificate"]['emissionGrade'] = energy_certificate_tags[1].text
            else: 
                features_dictionary[id]["energyCertificate"]['inProgress'] = True

            media_elements = soup_property_html_page.find_all("div", {"class": "masonry__item"})
            for media_element in media_elements:
                media_type = media_element.get("data-media-type")
                if media_type == 'Photo':
                    src = media_element.find('img').get('src')
                    if src:
                        features_dictionary[id]['multimedia']['images'].append(src)
                    else:
                        features_dictionary[id]['multimedia']['images'].append(media_element.find('img').get('data-src'))
                    continue
                
                if media_type == 'Video':
                    features_dictionary[id]['multimedia']['videos'].append(media_element.find('img').get('src'))
                    continue

                if media_type == 'FloorPlan':
                    features_dictionary[id]['multimedia']['plans'].append(media_element.find('img').get('src'))
                    continue


            tour = soup_property_html_page.find("a", {"class": "masonry__item"})
            if tour:
                features_dictionary[id]['multimedia']['virtualTour'] = tour.get('href')
                
            for element in elements_content:
                soup_features_feature = soup_property_html_page.find_all("div", {"class": "features__feature"})

                for feature in soup_features_feature:
                    soup_label = feature.find(class_='features__label')
                    soup_value = feature.find(class_='features__value')

                    label = soup_label.text

                    if not label in data_from_web_dictionary:
                        continue

                    if tag in data_from_web_dictionary:
                        features_dictionary[id]["features"][data_from_web_dictionary[tag]] = True
                        continue

                    if data_from_web_dictionary[label] in features_dictionary[id]["features"]:
                        features_dictionary[id]["features"][data_from_web_dictionary[label]] = True
                        continue
                    
                    if soup_value:
                        value = soup_value.text
                        if data_from_web_dictionary[label] == 'orientations':
                            features_dictionary[id]['orientations'] = value.split()
                        else:
                            value_int = get_numbers(value)
                            features_dictionary[id][data_from_web_dictionary[label]] = value_int
                    else: 
                        features_dictionary[id][data_from_web_dictionary[label]] = True
            print(features_dictionary[id])

        data_all_properties = {}
        index = 1
        for property in properties:
            data_all_properties[index] = features_dictionary[property["id"]]
            index += 1

        return data_all_properties

pisos_scraper = PisosScraper()
data_properties = pisos_scraper.scrape_data('https://www.pisos.com/venta/pisos-cadiz/')
js = json.dumps(data_properties)
fp = open ('scraped_properties.json', 'w')
fp.write(js)
fp.close()
