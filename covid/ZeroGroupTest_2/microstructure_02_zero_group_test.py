"""
Using the zero group microstructure
TODO: Campaign gives RASV to everyone in household group 0 at 100% effective in environmental route (dayjob)
TODO: Campaign gives OutbreakIndividual to everyone in household group 0

Run sim

TODO: Analyzer pulls back InsetChart.json
OBSERVE: Number of infections given by OutbreakIndividual == Number of RASV interventions given
VERIFY: Total number of infections never increases after outbreak:
1. Only people infected are in zero group
2. Zero group people do not transmit in environmental route
3. Zero group people _can_ not transmit in contact route (zero group modifier)
"""

from globals_zero_group import ERADICATION_PATH, SIM_CONFIG_PATH, SPOPS_ROOT
import os, json, shutil

from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.download_analyzer import DownloadAnalyzer
from idmtools.core import ItemType
from emodpy.emod_task import EMODTask

FINAL_DEMOGRAPHICS_FILENAME = 'demographics-microstructure.json'
FINAL_STATEFILE_FULLNAME = 'state-microstructure.dtk'
SEED_INFECTION = "campaign.json"
COVID_CONFIG_FILENAME = "covid_config.json"
FINAL_CONFIG = "config_02.json"
INPUTS_COVID_CONFIGFILE = os.path.join(
    SIM_CONFIG_PATH,
    COVID_CONFIG_FILENAME
)
TEST_results = "TEST_results.txt"


def create_config_file(base_config_file):
    with open(base_config_file) as infile:
        config_dict = json.load(infile)
    config_dict['parameters']['Demographics_Filenames'] = [FINAL_DEMOGRAPHICS_FILENAME]
    config_dict['parameters']['Serialized_Population_Filenames'] = [FINAL_STATEFILE_FULLNAME]
    config_dict['parameters']['Serialized_Population_Path'] = 'Assets'
    config_dict['parameters']['Enable_Interventions'] = 1
    config_dict['parameters']['Enable_Property_Output'] = 1
    config_dict['parameters']['Simulation_Duration'] = 65
    config_dict['parameters']["Enable_Heterogeneous_Intranode_Transmission"] = 1
    config_dict['parameters']["Minimum_End_Time"] = 0
    final_config_fullpath = os.path.join(SIM_CONFIG_PATH, FINAL_CONFIG)
    with open(final_config_fullpath, 'w') as outfile:
        json.dump(config_dict, outfile, indent=4, sort_keys=True)
    return final_config_fullpath


def run_microstructure_sim(config_fullpath, test_results):
    campaign_fullpath = os.path.join(SIM_CONFIG_PATH, SEED_INFECTION)
    platform = Platform('COMPS2')

    zerogroup_test_task = EMODTask.from_files(
        eradication_path=ERADICATION_PATH,
        config_path=config_fullpath,
        campaign_path=campaign_fullpath,
        demographics_paths=[FINAL_DEMOGRAPHICS_FILENAME]
    )

    statefile_asset = Asset(absolute_path=FINAL_STATEFILE_FULLNAME)
    zerogroup_test_task.common_assets.add_asset(statefile_asset)

    zerogroup_test_experiment = Experiment.from_task(
        task=zerogroup_test_task,
        name="DTK-Covid Test Stage 2"
    )

    platform.run_items(zerogroup_test_experiment)
    exp_id = zerogroup_test_experiment.id
    platform.wait_till_done(zerogroup_test_experiment)
    # delete output from previous run

    filenames = ['output/InsetChart.json']
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='output')]

    am = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    am.analyze()

    exp = platform.get_item(item_id=exp_id, item_type=ItemType.EXPERIMENT)
    sims = platform.get_children_by_object(exp)
    if len(sims) != 1:
        test_results.write(f"BAD: There should only be one sim in the experiment, but there are {len(sims)}, the "
                           f"test cannot continue. \n")
        exit()
    else:
        sim_id = sims[0].id  # this is the name of the folder in the output folder where the files are downloaded to
        return sim_id


def verify_no_new_infections(sim_id=None, test_results=None):
    local_success = True
    insetchart_path = os.path.join("output", sim_id, "InsetChart.json")
    with open(insetchart_path) as insetchart:
        icj = json.load(insetchart)["Channels"]
    new_infections = icj["New Infections"]["Data"]
    outbreak_day = 3
    for day, infections in enumerate(new_infections):
        if day > (outbreak_day - 1) and infections != 0:
            # new infections start with 0, days start with 1
            local_success = False
            test_results.write(f"BAD:There shouldn't be any new infections on day {day + 1}, "
                               f"after outbreak on {outbreak_day}, but there are {infections} new infections. \n")

    if local_success:
        test_results.write(f"GOOD: No new infections detected outside of the outbreak on day {outbreak_day}!\n")
    return local_success


if __name__ == "__main__":
    with open(TEST_results, "a") as test_results:
        test_results.write("Running ZeroGroupTest microstructure_02 script:\n")
        config_fullpath = create_config_file(base_config_file=INPUTS_COVID_CONFIGFILE)
        sim_id = run_microstructure_sim(config_fullpath, test_results)
        success = verify_no_new_infections(sim_id, test_results)
        if success:
            test_results.write("SUCCESS! ZeroGroupTest passed!")
        else:
            test_results.write("FAILURE! ZeroGroupTest didn't pass!")
    pass
