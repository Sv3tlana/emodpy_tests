#!/usr/bin/env python

import json
import os
import shutil

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer

from emodpy.emod_task import EMODTask
from globals_zero_group import ERADICATION_PATH, SIM_CONFIG_PATH

import emodpy_covid.config as config
import emodpy_covid.demog as demog

CANNED_CONFIG_FILENAME = "covid_config_stage1.json"
CANNED_DEMOGRAPHICS_FILENAME = "demographics.json"
COVID_CONFIG_FILENAME = "covid_config.json"

def create_canned_config():
    if os.path.isfile("schema.json"):
        os.unlink("schema.json")

    config.app("Eradication-bamboo.exe") # Calls emodpy_covid to make some config files

    destination_filepath = os.path.join(SIM_CONFIG_PATH, CANNED_CONFIG_FILENAME)
    shutil.move(CANNED_CONFIG_FILENAME,
                destination_filepath)

    simulation_destination_filepath = os.path.join(SIM_CONFIG_PATH, COVID_CONFIG_FILENAME)
    shutil.move(COVID_CONFIG_FILENAME, simulation_destination_filepath)

    return destination_filepath


def create_canned_demog():
    demog.get_demog() # Calls emodpy_covid to get a demographics file

    destination_filepath = os.path.join(SIM_CONFIG_PATH, CANNED_DEMOGRAPHICS_FILENAME)
    shutil.move(CANNED_DEMOGRAPHICS_FILENAME,
                destination_filepath)

    return destination_filepath


def generate_environmental_spop_file(
        config_filepath,
        demographics_filepath
):
    # Create the platform
    platform = Platform('COMPS2')

    params = None
    with open(config_filepath) as infile:
        params = json.load(infile)["parameters"]

    serialization_timesteps = params["Serialization_Time_Steps"]

    make_resources_task = EMODTask.from_files(
        eradication_path=ERADICATION_PATH,
        config_path=config_filepath,
        campaign_path=os.path.join(SIM_CONFIG_PATH, "campaign_seed_infection.json"),
        demographics_paths=[
            demographics_filepath
        ]
    )
    experiment = Experiment.from_task(task=make_resources_task,
                                      name="DTK-COVID examples 00 canned environmental sim statefile")

    platform.run_items(experiment)
    platform.wait_till_done(experiment)

    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.\nDownloading dtk serialization files from Comps:\n")

    # Cleanup the output path
    output_path = 'spop_files'

    # We want to download all the dtk state files and the InsetChart.json
    filenames = []
    for serialization_timestep in serialization_timesteps:
        filenames.append(f"output/state-{serialization_timestep:05}.dtk")
    filenames.append('output/InsetChart.json')

    for f in filenames:
        filepath = os.path.join(output_path, f)
        if os.path.isfile(filepath):
            os.unlink(filepath)

    # Create the analyze manager
    am = AnalyzeManager(platform=platform)
    am.add_item(experiment)
    am.add_analyzer(DownloadAnalyzer(filenames=filenames, output_path=output_path))

    # Analyze
    am.analyze()
    pass

if __name__ == "__main__":
    config_filepath = create_canned_config()
    demog_filepath = create_canned_demog()

    generate_environmental_spop_file(
        config_filepath=config_filepath,
        demographics_filepath=demog_filepath
    )
    pass
