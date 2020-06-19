#!/usr/bin/env python
import os
import json
from stravalib import Client, exc
from requests.exceptions import ConnectionError
import csv
import shutil
import time
from datetime import datetime, timedelta
import sys
import pandas as pd
import random

access_token = sys.argv[1]


def convert_json_to_csv(filepath):
    for file in os.listdir(filepath):
        work_file = os.path.join(filepath + '/', file)
        with open(work_file) as json_file:
            dct = json.load(json_file)
            df = pd.DataFrame([dct])
            df.to_csv('../json_to_csv/' + str(file.split('.')[0]) + '.csv', index=False)


def get_strava_access_token():
    global access_token

    if access_token is not None:
        print('Found access token')
        return access_token

    access_token = os.environ.get('STRAVA_UPLOADER_TOKEN')
    if access_token is not None:
        print('Found access token')
        return access_token

    print('Access token not found. Please set the env variable STRAVA_UPLOADER_TOKEN')
    exit(1)


def get_strava_client():
    token = get_strava_access_token()
    client = Client()
    client.access_token = token
    return client


def increment_activity_counter(counter):
    if counter >= 599:
        print("Upload count at 599 - pausing uploads for 15 minutes to avoid rate-limit")
        time.sleep(900)
        return 0

    counter += 1
    return counter


# designates part of day for name assignment, matching Strava convention for GPS activities
def strava_day_converstion(hour_of_day):
    if 3 <= hour_of_day <= 11:
        return "Morning"
    elif 12 <= hour_of_day <= 4:
        return "Afternoon"
    elif 5 <= hour_of_day <= 7:
        return "Evening"

    return "Night"


def activity_translator(activity_id):
    input_file = csv.DictReader(open("activity_translator_data.csv"))
    for row in input_file:
        if int(row['id']) == int(activity_id):
            return row['activity']


# Get a small range of time. Note runkeeper does not maintain timezone
# in the CSV, so we must get about 12 hours earlier and later to account
# for potential miss due to UTC
def get_date_range(time, hourBuffer=12):
    if type(time) is not datetime:
        raise TypeError('time arg must be a datetime, not a %s' % type(time))

    return {
        'from': time + timedelta(hours=-1 * hourBuffer),
        'to': time + timedelta(hours=hourBuffer),
    }


def activity_exists(client, activity_name, start_time):
    date_range = get_date_range(start_time)

    print("Getting existing activities from [" + date_range['from'].isoformat() + "] to [" + date_range[
        'to'].isoformat() + "]")

    activities = client.get_activities(
        before=date_range['to'],
        after=date_range['from']
    )

    for activity in activities:
        if activity.name == activity_name:
            return True

    return False


def create_activity(client, activity_id, duration, distance, start_time, strava_activity_type):
    # convert to total time in seconds

    day_part = strava_day_converstion(start_time.hour)

    activity_name = day_part + " " + strava_activity_type + " (Manual)"

    if activity_exists(client, activity_name, start_time):
        print('Activity [' + activity_name + '] already created, skipping')
        return

    print("Manually uploading [" + activity_id + "]:[" + activity_name + "]")

    try:
        upload = client.create_activity(
            name=activity_name,
            start_date_local=start_time,
            elapsed_time=duration,
            distance=distance,
            activity_type=strava_activity_type
        )

        print("Manually created " + activity_id)
        return True

    except ConnectionError as err:
        print("No Internet connection: {}".format(err))
        exit(1)


def upload_gpx(client, gpxfile):
    if not os.path.isfile(gpxfile):
        print("No file found for " + gpxfile + "!")
        return False

    print("------------------------------------------------------------------")
    print("Uploading " + gpxfile)

    try:
        upload = client.upload_activity(
            activity_file=open(gpxfile, 'r'),
            data_type='gpx',
            private=False
        )

    except exc.ActivityUploadFailed as err:
        errStr = str(err)
        # deal with duplicate type of error, if duplicate then continue with next file, else stop
        if errStr.find('duplicate of activity'):
            print("Duplicate File " + gpxfile + " is already uploaded.")
            return False
        else:
            print("Another ActivityUploadFailed error: {}".format(err))
            exit(1)

    except ConnectionError as err:
        print("No Internet connection: {}".format(err))
        exit(1)

    try:
        upResult = upload.wait()
    except exc.ActivityUploadFailed as err:
        errStr = str(err)
        # deal with duplicate type of error, if duplicate then continue with next file, else stop
        if errStr.find('duplicate of activity'):
            print("Duplicate File " + gpxfile + " is already uploaded.")
            return True
        else:
            print("Another ActivityUploadFailed error: {}".format(err))
            exit(1)

    print("Uploaded " + gpxfile + " - Activity id: " + str(upResult.id))
    return True


def main():
    files_path = sys.argv[3].split(',')
    client = get_strava_client()

    print('Connecting to Strava')
    athlete = client.get_athlete()
    print("Now authenticated for " + athlete.firstname + " " + athlete.lastname)

    activity_counter = 0
    completed_activities = []

    if sys.argv[2] == 'json' or sys.argv[2] == 'csv':
        if sys.argv[2] == 'json':
            convert_json_to_csv(sys.argv[3])
            data_path = '../json_to_csv'
        if sys.argv[2] == 'csv':
            data_path = files_path
        for file in os.listdir(data_path):
            csv_file = os.path.join(data_path + '/', file)
            activities = csv.DictReader(open(csv_file))
            for row in activities:
                strava_activity_type = activity_translator(int(row['sport_type_id']))
                start_time = datetime.strptime(str(datetime.utcfromtimestamp(int(row['start_time'][:-3])).strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
                print(start_time)
                duration = int(row['end_time'][:-3])-int(row['start_time'][:-3])
                distance = int(row['distance'])
                activity_id = str(row['id'])
                if strava_activity_type is not None:
                    if create_activity(client, activity_id, duration, distance, start_time, strava_activity_type):
                        completed_activities.append(activity_id)
                        activity_counter = increment_activity_counter(activity_counter)
                else:
                    print('Invalid activity type ' + str(row['Type']) + ', skipping')

    elif sys.argv[2] == 'gpx':
        for file in os.listdir(sys.argv[3] + '/'):
            gpxfile = os.path.join(sys.argv[3] + '/', file)

            if upload_gpx(client, gpxfile):
                activity_counter = increment_activity_counter(activity_counter)
    else:
        print("Wrong data path. Make sure you are using the correct path to file.")
    print("Complete! Created [" + str(activity_counter) + "] activities.")


if __name__ == '__main__':
    main()
