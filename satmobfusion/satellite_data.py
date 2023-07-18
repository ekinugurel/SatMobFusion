import os
import re
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import time
from shapely.geometry import Polygon

import satmobfusion.convenience as c

from api_keys import PLANET_API_KEY


def get_planet_api_request(locs, location, max_cloud_cover, item_type):
    geojson_geometry = {
        "type": "Polygon",
        "coordinates": [c.get_rectangular_polygon_from_bounding_box(*locs.loc[location, ["lon_min", "lon_max", "lat_min", "lat_max"]].values)]
    }

    # get images that overlap with our AOI
    geometry_filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config": geojson_geometry
    }

    # get images acquired within a date range
    #Tulsa, OK: 2020-05-15
    #Champaign, IL: 2020-04-06-08
    date_range_filter = {
        "type": "DateRangeFilter",
        "field_name": "acquired",
        "config": {
            # "gte": "2020-05-12T00:00:00.000Z",
            # "lte": "2020-05-19T00:00:00.000Z"
            "gte": f"{locs.loc[location, 'date_min'].date()}T00:00:00.000Z",
            "lte": f"{locs.loc[location, 'date_max'].date()}T00:00:00.000Z",
        }
    }

    # only get images which have <50% cloud coverage
    cloud_cover_filter = {
        "type": "RangeFilter",
        "field_name": "cloud_cover",
        "config": {
            "lte": 0.2
        }
    }

    # combine our geo, date, cloud filters
    combined_filter = {
        "type": "AndFilter",
        "config": [geometry_filter, date_range_filter, cloud_cover_filter]
    }

    # API request object
    search_request = {"item_types": [item_type], "filter": combined_filter}

    return search_request,geojson_geometry


def check_image_availability(search_request, api_key):
    # fire off the POST request
    search_result = \
        requests.post(
            'https://api.planet.com/data/v1/quick-search',
            auth=HTTPBasicAuth(PLANET_API_KEY, ''),
            json=search_request)

    geojson = search_result.json()

    # let's look at the first result
    if len(list(geojson.items())[1][1]) > 0:
        print(f"A total of {len(list(geojson.items())[1][1])} images were found in that AOI and date range.\n")
        print("First image in that AOI and date range:")
        print(list(geojson.items())[1][1][0])
    else:
        print("No images in that AOI and date range.")

    return geojson

def get_suitable_image_IDs(locs, location, image_ids, geojson, geojson_geometry, folder):
    images_df = pd.DataFrame(index=image_ids, columns=["date_acquired", "is_pre", "is_post", "diff_to_date_event", "coverage_of_AOI", "combined_metric"])
    date_event_begin = locs.loc[location, "date_event_begin"]
    date_event_end = locs.loc[location, "date_event_end"]
    AOI_polygon = Polygon(geojson_geometry['coordinates'][0])
    for image_id in image_ids:
        # print("\n"+image_id)
        images_df.loc[image_id, "date_acquired"] = pd.to_datetime(geojson['features'][image_ids.index(image_id)]['properties']['acquired']).tz_convert(locs.loc[location, "timezone"])
        images_df.loc[image_id, "is_pre"] = images_df.loc[image_id, "date_acquired"] < date_event_begin
        images_df.loc[image_id, "is_post"] = images_df.loc[image_id, "date_acquired"] > date_event_end
        if images_df.loc[image_id, "is_pre"]:
            images_df.loc[image_id, "diff_to_date_event"] = images_df.loc[image_id, "date_acquired"] - date_event_begin
        elif images_df.loc[image_id, "is_post"]:
            images_df.loc[image_id, "diff_to_date_event"] = images_df.loc[image_id, "date_acquired"] - date_event_end
        else: #image data acquired is during event
            images_df.loc[image_id, "diff_to_date_event"] = pd.Timedelta(0)
        satellite_polygon = Polygon(geojson['features'][image_ids.index(image_id)]['geometry']['coordinates'][0])
        intersection = satellite_polygon.intersection(AOI_polygon)
        images_df.loc[image_id, "coverage_of_AOI"] = intersection.area/AOI_polygon.area

        #a low combined metric is more desirable
        #25% (percentage points) more coverage of AOI is worth selecting an image that is 1 day further away from the event
        images_df.loc[image_id, "combined_metric"] = abs(images_df.loc[image_id, "diff_to_date_event"].total_seconds()/60/60/24) - 4*images_df.loc[image_id, "coverage_of_AOI"]
        # print(images_df.loc[image_id, ["diff_to_date_event", "coverage_of_AOI", "combined_metric"]].values)

    images_df.sort_values(["is_post", "combined_metric"]).to_csv(folder+"images_df.csv")

    image_id_pre = images_df[images_df["is_pre"]].sort_values("combined_metric", ascending=True).index[0]
    image_id_post = images_df[images_df["is_post"]].sort_values("combined_metric", ascending=True).index[0]
    IDs = [image_id_pre, image_id_post]

    print(IDs)

    return IDs

def download_suitable_images(locs, location, IDs, api_key, asset_type, item_type, folder):
    fn_suffix = {0: "pre", 1: "post"}
    # fn_suffix = {"0_0": "pre", "0_1": "pre_meta", "1_0": "post", "1_1": "post_meta"}

    for i,ID in enumerate(IDs):
        print(ID)
        id_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, ID)

        # Returns JSON metadata for assets in this ID. Learn more: planet.com/docs/reference/data-api/items-assets/#asset
        result = requests.get(id_url, auth=HTTPBasicAuth(PLANET_API_KEY, ''))

        # List of asset types available for this particular satellite image
        print("\tAvailable asset types for this satellite image:", result.json().keys())
        print("\tAsset type we will use:", asset_type)

        # This is "inactive" if the "ortho_analytic_4b" asset has not yet been activated; otherwise 'active'
        # print(result.json()[asset_type]['status'])

        # Parse out useful links
        # for j,asset_typee in enumerate([asset_type,asset_type+"_xml"]):
        links = result.json()[asset_type]["_links"]
        self_link = links["_self"]
        activation_link = links["activate"]

        # Request activation of the asset
        activate_result = requests.get(activation_link, auth=HTTPBasicAuth(PLANET_API_KEY, ''))
        print("\tWaiting for activation...", end="")
        while(True):
            activation_status_result = requests.get(self_link, auth=HTTPBasicAuth(PLANET_API_KEY, ''))
            if activation_status_result.json()["status"] != "active":
                time.sleep(2)
                print(".", end="")
            else:
                print(activation_status_result.json()["status"])
                break

        # Image can be downloaded by making a GET with your Planet API key, from here:
        download_link = activation_status_result.json()["location"]
        print("\tDownload link:", download_link)

        # Download the image
        response = requests.get(download_link, stream=True)
        print("\tStatus code:", response.status_code)
        # print("full url:", response.url)
        # print("text:", response.text)
        fn = re.findall("filename=(.+)", response.headers['content-disposition'])[0][1:-1]
        # locs.loc[location, "fn_satellite_"+fn_suffix[f"{i}_{j}"]] = fn
        locs.loc[location, "fn_satellite_"+fn_suffix[i]] = fn
        if os.path.isfile(folder+fn):
            print("\tImage already downloaded, skipping download.")
        else:
            with open(folder+fn, "wb") as fd:
                fd.write(response.content)
                for chunk in response.iter_content(chunk_size=1024*1024):
                    fd.write(chunk)
        print("\n")
    locs.to_csv("config/locations.csv")
