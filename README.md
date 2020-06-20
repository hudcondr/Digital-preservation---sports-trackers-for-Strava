# Digital-preservation - Adidas Running migration tool to strava


## Introduction

This is a python implementation of a migration tool for the Adidas Running data to Strava. The migration works in a way that the script takes files with Adidas Running activity data and creates a new activity with this data. The data is the uploaded to Strava environment in a form of POST request.

## Prerequisites

All dependencies necessary for running this app are included in `requirements.txt` file. Before executing the scripts, run

```bash
$ pip install -r requirements.txt
```

## Authorization
Application needs to have an access to user's profile. This is done by running the code:
```bash
$ python get_client_access_token.py <client_id> <client_secret>
```
Note, that `client_id` and `client_secret` are permanent tokens and can be found in a personal profile of a user, [here](https://www.strava.com/settings/api). This is an overview of a page where we can find this information.

![Alt text](/images/api_profile.png?raw=true)

Running the code will pop up a Strava link which requires an authorization confirmation for our application - among other things, read and write permissions. Here, the user needs to click "Authorize" button (see below).

![Alt text](/images/authorization_page.png?raw=true)

After authorizing the necessary rights, a user is redirected to another page, where a code appears. This needs to be run as a first argument for `runtastic_strava_migration_tool.py`. The redirect page can look like the one below.


![Alt text](/images/pop_up.png?raw=true)

## Migration

To migrate user's Runtastic data to Strava, the following command needs to be run:
```bash
$ python runtastic_strava_migration_tool.py <access_token> <data_type> <path>
```

Arguments:

* "access_token" is received from previous step,
* "data_type" is one (and only one) of the json|csv|gpx options,
* "path" is a relative path to data a user wants to migrate

Example:
```bash
$ python runtastic_strava_migration_tool.py 75c63be434b56ac4dd279592c3462b4262e43f5b gpx ../data/Sport-sessions/GPS-data/
```
The script automatically reads all relevant data in the particular directory.

## Result

To check the outcome of the migration, a user can visit [activity section of the personal profile](https://www.strava.com/athlete/training). Below we can see an example of migrated GPS data of an activity.

![Alt text](/images/example_activity_map.png?raw=true)

If we scroll down, we can also see particular checkpoints of this activity.

![Alt text](/images/example_activity_data_points.png?raw=true)


## Contributors

[Ondrej Hudcovic](https://orcid.org/0000-0001-5208-7222)

[Tomas Drietomsky](https://orcid.org/0000-0002-3814-6000)

## License

[MIT](/LICENSE)
