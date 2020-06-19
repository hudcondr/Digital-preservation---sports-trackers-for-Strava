# Digital-preservation - migration tool - from runtastic to strava


## Introduction

## Prerequisites

Use pip install requirements.txt

## Get your Access Token

Run code 

python get_client_access_token.py "client_id" "client_secret" - client_id & client_secret can be found at https://www.strava.com/settings/api 

[screenshot]

Running this code will pop up strava webpabe and will ask you to authorize access.
For purposes of using the migration tool, you have to click authorize.
After that, a code will appear on the webpage. Save this code in clipboard and use it in
runtastic_to_strava_migration_tool.

[screenshot]

To migrate your Runtastic data to Strava, you have to run 
python runtastic_strava_migration_tool.py "access_token" "data source type" "path to files"
where:
* access_token is received from previous step
* data source type can be : json, csv or gpx
* and path to files is path in this format : "../data/Sport-sessions/activity-data" - make sure to divide your data in folders by their data type.

In strava, you can manually update activities, but only limited attributes:
  name,
  start_date_local,
  elapsed_time,
  distance,
  activity_type

