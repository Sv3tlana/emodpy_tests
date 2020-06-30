import os, json, shutil

from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from globals_zero_group import ERADICATION_PATH, SIM_CONFIG_PATH, SPOPS_ROOT
from emodpy.emod_task import EMODTask

import emodpy_covid.microstructure.change_ser_pop as change_serialized_population

CANNED_DEMOGRAPHICS_FILENAME = "demographics.json"
CANNED_STATEFILE_FILENAME = "state-00000.dtk"
COVID_CONFIG_FILENAME = "covid_config.json"

from globals_zero_group import ERADICATION_PATH, SIM_CONFIG_PATH, SPOPS_ROOT

INPUTS_CANNED_DEMOGRAPHICS = os.path.join(
    SIM_CONFIG_PATH,
    CANNED_DEMOGRAPHICS_FILENAME
)
INPUTS_CANNED_STATEFILE = os.path.join(
    SIM_CONFIG_PATH,
    CANNED_STATEFILE_FILENAME
)

INPUTS_COVID_CONFIGFILE = os.path.join(
    SIM_CONFIG_PATH,
    COVID_CONFIG_FILENAME
)
try:
    random_sim_id = os.listdir(SPOPS_ROOT)[-2]  # -1 will be README.txt
    SPOP_FOLDER = os.path.join(SPOPS_ROOT, random_sim_id)
except Exception:
    raise FileNotFoundError(f"Couldn't find a folder under {SPOPS_ROOT},"
                            f" try running 00_generate_spop_file.py first.")

FINAL_DEMOGRAPHICS_FILENAME = 'demographics-microstructure.json'
FINAL_STATEFILE_FULLNAME = 'state-microstructure.dtk'


def add_microstructure_to_statefile_and_demographics(
        starting_statefile_fullpath,
        starting_demographics_fullpath
):
    change_serialized_population.change_ser_pop(
        path=starting_statefile_fullpath,
        input_demog=starting_demographics_fullpath,
        output_demog=FINAL_DEMOGRAPHICS_FILENAME,
        save_file_path=FINAL_STATEFILE_FULLNAME
    )

def create_config_file(base_config_file):
    with open(base_config_file) as infile:
        config_dict = json.load(infile)
    config_dict['parameters']['Demographics_Filenames'] = [FINAL_DEMOGRAPHICS_FILENAME]
    config_dict['parameters']['Serialized_Population_Filenames'] = [FINAL_STATEFILE_FULLNAME]
    config_dict['parameters']['Serialized_Population_Path'] = 'Assets'
    config_dict['parameters']['Enable_Interventions'] = 1
    config_dict['parameters']['Enable_Property_Output'] = 1
    config_dict['parameters']['Simulation_Duration'] = 100
    final_config_filename = "covid_config_stage2.json"
    final_config_fullpath = os.path.join(SIM_CONFIG_PATH, final_config_filename)
    with open(final_config_fullpath, 'w') as outfile:
        json.dump(config_dict, outfile, indent=4, sort_keys=True)
    return final_config_fullpath

def run_microstructure_sim(config_file_fullpath):
    campaign_fullpath = os.path.join(SIM_CONFIG_PATH, "campaign_seed_infection.json")
    platform = Platform('COMPS2')

    zerogroup_test_task = EMODTask.from_files(
        eradication_path=ERADICATION_PATH,
        config_path=config_file_fullpath,
        campaign_path=campaign_fullpath,
        demographics_paths=[FINAL_DEMOGRAPHICS_FILENAME]
    )

    statefile_asset = Asset(absolute_path=FINAL_STATEFILE_FULLNAME)
    zerogroup_test_task.common_assets.add_asset(statefile_asset)

    zerogroup_test_experiment = Experiment.from_task(
        task=zerogroup_test_task,
        name="DTK-Covid examples 01 canned microstructure"
    )

    platform.run_items(zerogroup_test_experiment)
    platform.wait_till_done(zerogroup_test_experiment)

if __name__ == "__main__":
    if not os.path.isfile(INPUTS_CANNED_DEMOGRAPHICS):
        raise EnvironmentError("You need to run microstructure_00 first")
    if not os.path.isfile(INPUTS_CANNED_STATEFILE):
        found_statefile = os.path.join(SPOP_FOLDER, CANNED_STATEFILE_FILENAME)
        if os.path.isfile(found_statefile):
            shutil.move(found_statefile, INPUTS_CANNED_STATEFILE)
        else:
            raise EnvironmentError("Couldn't find statefile either in inputs or in local folder")
    add_microstructure_to_statefile_and_demographics(
        starting_statefile_fullpath=INPUTS_CANNED_STATEFILE,
        starting_demographics_fullpath=INPUTS_CANNED_DEMOGRAPHICS
    )
    config_fullpath = create_config_file(base_config_file=INPUTS_COVID_CONFIGFILE)
    run_microstructure_sim(config_file_fullpath=config_fullpath)

    run_microstructure_sim(
        config_filepath=config_fullpath,
        demographics_filepath=INPUTS_CANNED_DEMOGRAPHICS
    )
    pass
