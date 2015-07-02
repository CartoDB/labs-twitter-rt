import random
import string
import time
from datetime import datetime, timedelta
import os
from powertrack.api import *
from cartodb import CartoDBAPIKey, CartoDBException

config = ConfigParser.RawConfigParser()
config.read("app.conf")

APP_NAME= config.get('general','app_name')
IMPORT_API_ENDPOINT = config.get('cartodb', 'import_api_endpoint')
ACCOUNT_NAME = config.get('cartodb', 'account_name')
API_KEY = config.get('cartodb', 'api_key')
TABLE_NAME = config.get('cartodb', 'table_name')
RUN_AFTER_S = int(config.get('intervals', 'run_after_s'))

p = PowerTrack(api="search")
cl = CartoDBAPIKey(API_KEY, ACCOUNT_NAME)

# Split categories
categories = [cat.split(" ") for cat in config.get('twitter','categories').split("|")]


print ("======================================")
print ("   Starting script {} for user {}".format(APP_NAME,ACCOUNT_NAME))
print ("======================================")


# Get tweets from GNIP

while 1:
    # Read the start timestamp
    with open("{table_name}_next.conf".format(table_name=TABLE_NAME), "r") as conf:
        conf = json.loads(conf.read())
        start_timestamp = datetime.strptime(conf["start_timestamp"], "%Y%m%d%H%M%S")

    # Set the end timestamp as now
    end_timestamp = datetime.utcnow()

    print(start_timestamp, end_timestamp)

    tmp_table_name = TABLE_NAME + "_" + ''.join(random.choice(string.ascii_uppercase) for _ in range(25))
    tmp_table_filename = tmp_table_name

    # Call a new PowerTrack job
    for i, category in enumerate(categories):
        new_job = p.jobs.create(start_timestamp, end_timestamp, tmp_table_name, category)
        new_job.export_tweets(category=i + 1, append=False if i == 0 else True)

    # Now, because we can't use ogr2ogr, here comes the HACK!

    # 1) Import file into cartodb.com

    files = {'file': open(tmp_table_name + '.csv', 'rb')}

    r = requests.post(IMPORT_API_ENDPOINT, files=files, params={"api_key": API_KEY})
    response_data = r.json()
    print ("SUCCESS", response_data["success"])

    state = "uploading"
    item_queue_id = response_data["item_queue_id"]
    while state != "complete" and state != "failure":
        time.sleep(5)
        try:
            r = requests.get(IMPORT_API_ENDPOINT + item_queue_id, params={"api_key": API_KEY})
        except ValueError:
            continue
        else:
            response_data = r.json()
            state = response_data["state"]
            print (response_data)

    if state == "failure":
        continue

    tmp_table_name = response_data["table_name"]  # Just in case it changed during import
    print ("TMP_TABLE_NAME", tmp_table_name)

    # 2) Append new data from temp table to real table

    try:
        print (cl.sql("INSERT INTO {account_name}.{table_name} (actor_displayname,actor_followerscount,actor_friendscount,"
            "actor_id,actor_image,actor_languages,actor_link,actor_links,actor_listedcount,actor_location,actor_objecttype,"
            "actor_postedtime,actor_preferredusername,actor_statusescount,actor_summary,actor_twittertimezone,actor_utcoffset,"
            "actor_verified,body,category_name,category_terms,favoritescount,generator_displayname,generator_link,geo,gnip,id,"
            "inreplyto_link,link,location_displayname,location_geo,location_link,location_name,location_objecttype,"
            "location_streetaddress,object_id,object_link,object_objecttype,object_postedtime,object_summary,object_type,"
            "postedtime,provider_displayname,provider_link,provider_objecttype,retweetcount,the_geom,twitter_entities,"
            "twitter_filter_level,twitter_lang,verb,cartodb_id) SELECT actor_displayname,actor_followerscount,actor_friendscount,"
            "actor_id,actor_image,actor_languages,actor_link,actor_links,actor_listedcount,actor_location,actor_objecttype,"
            "actor_postedtime,actor_preferredusername,actor_statusescount,actor_summary,actor_twittertimezone,actor_utcoffset,"
            "actor_verified,body,category_name,category_terms,favoritescount,generator_displayname,generator_link,geo,gnip,id,"
            "inreplyto_link,link,location_displayname,location_geo,location_link,location_name,location_objecttype,"
            "location_streetaddress,object_id,object_link,object_objecttype,object_postedtime,object_summary,object_type,"
            "postedtime,provider_displayname,provider_link,provider_objecttype,retweetcount,the_geom,twitter_entities,"
            "twitter_filter_level,twitter_lang,verb,nextval('{table_name}_cartodb_id_seq') as cartodb_id "
            "FROM {account_name}.{tmp_table_name}".format(table_name=TABLE_NAME, tmp_table_name=tmp_table_name, account_name=ACCOUNT_NAME)))
    except CartoDBException as e:
        print ("some error ocurred", e)
        continue

    with open("{table_name}_next.conf".format(table_name=TABLE_NAME), "w") as conf:
        conf.write(json.dumps({"start_timestamp": end_timestamp.strftime("%Y%m%d%H%M%S")}))

    # 3) Delete temporary table
    try:
        print "Deleting temporal table {}".format(tmp_table_name)
        print cl.sql("DROP TABLE %s" % tmp_table_name)
    except CartoDBException as e:
        print ("some error ocurred", e)

    try:
        os.remove(tmp_table_filename + '.csv')
    except OSError:
        pass

    # Moving to sleep
    print("Sleeping will awake after {} minutes...".format(int(RUN_AFTER_S/60)))
    print ("======================================")
    time.sleep(RUN_AFTER_S)
    print("Awake...")