import sqlite3
import json

def application():
    # read outbreak time from campaign.json
    outbreak_timestep = -1
    with open("zero_group_report.txt", "w") as reportfile:
        with open ('campaign.json') as infile:
            events = json.load(infile)["events"]
            if len(events) > 1:
                reportfile.write(f"Weird! Should only be 1 event, but got {len(events)}.")
            else:
                reportfile.write("Cool. Expected one event and found one.")
            outbreak_timestep = events[0]["Start_Day"]

        with sqlite3.connect("simulation_events.db") as conn:
            cur = conn.cursor()
            query =