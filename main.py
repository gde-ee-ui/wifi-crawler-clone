import threading
import urllib3
import time
import os
import json
import pytz

from AccessPoint.controllers.ArubaAP import ArubaAP
from UseCase.EnergySaving import EnergySaving
from Switch.Controller.HPE import HPE
from Connection.ArubaConnection import *
from Connection.InfluxConnection import *
from UseCase.EnergySaving import EnergySaving
from Connection.InfluxConnection import *
from datetime import datetime


def load_credentials(file_path):
    """
    Load credentials from a YAML file.

    :param file_path: Path to the YAML file.
    :return: Parsed YAML data as a dictionary.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def update_influxDB_measurement():
    credential = get_credentials(True)
    update_measurement(credential, "aruba-test", "ap_usage",
                       "APs-usage", new_fields=["total-APs"])


def convert_taiwan_time(utc_time):
    # Set the timezone to UTC
    utc_time = utc_time.replace(tzinfo=pytz.utc)

    # Convert to Asia/Taipei time
    taiwan_time = utc_time.astimezone(pytz.timezone('Asia/Taipei'))

    # Convert to ISO format
    return taiwan_time.strftime("%Y-%m-%d %H:%M:%S")


def crawler(functions, activities, interval, use_case):
    while True:
        # Set the use-case timestamp in the environment variables
        utc_time = datetime.utcnow()
        os.environ[f'{use_case} timestamp'] = utc_time.isoformat()

        start = time.time()
        for idx, function in enumerate(functions):
            print(f"[{datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] Start \"{activities[idx]}\" data crawling...")
            function()

        end = time.time()
        elapsed = min((end - start), interval)
        print(
            f"[{datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] Finished Thread#{idx + 1}: \"{thread['name']}\" data crawling within {elapsed:.2f} seconds")
        # Make sure the sleep time is not negative value
        time.sleep(interval - elapsed)


def old_main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Load the credentials from the YAML file
    credentials = load_credentials(os.getcwd() + "/credentials.yml")

    # Get the intervals for each use-case
    intervals = {}
    for use_case in credentials['use-cases']:
        intervals[use_case['name']] = use_case['interval']

    # Instance of each Crawler type
    aruba_ap = ArubaAP()
    hpe_switch = HPE()

    while True:
        threads = [
            {"object": threading.Thread(target=crawler, args=(
                [aruba_ap.get_adjacent_aps], ["Adjacent Access Points"], intervals['Rogue-AP'], "Rogue-AP")),
                "name": "Rogue-AP"},
            {"object": threading.Thread(target=crawler, args=([aruba_ap.get_aps_usage, hpe_switch.get_poe_usage],
                                                              ['Access Point Usage',
                                                               "Switch PoE Usage"],
                                                              intervals['Energy Saving'], "Energy Saving"),),
             "name": "Energy Saving"}
        ]

        # Start the threads
        for idx, thread in enumerate(threads):
            print(
                f"[{datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] Start Thread#{idx + 1}: \"{thread['name']}\" data crawling...")

            thread['object'].start()

        # Wait for all threads to finish
        for thread in threads:
            thread['object'].join()


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # EnergySaving().crawl()
    hpe = HPE()
    es = EnergySaving()

    es.main()

    # check_connection()
