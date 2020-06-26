
# Use previous spop file. If not there, just raise an exception and stop
# Modify the statefile and make the demographics overlay locally (avoid emodpy_covid dependency on cluster)
# Add all the stuff to assets
# Run simulation with a sweep of run_number, perhaps households for outbreaks (random.choice(len(households))

import json
import os

from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.emod_task import EMODTask

from globals_zero_group import ERADICATION_PATH, SIM_CONFIG_PATH, SPOPS_ROOT
demographics_start_filename = "demographics.json"
demographics_end_filename = "demographics-microstructure.json"

demographics_start_fullpath = os.path.join(SIM_CONFIG_PATH, demographics_start_filename)
demographics_end_fullpath = os.path.join(SIM_CONFIG_PATH, demographics_end_filename)

try:
    random_sim_id = os.listdir(SPOPS_ROOT)[-2]  # -1 will be README.txt
    SPOP_FOLDER = os.path.join(SPOPS_ROOT, random_sim_id)
except Exception:
    raise FileNotFoundError(f"Couldn't find a folder under {SPOPS_ROOT},"
                            f" try running 00_generate_spop_file.py first.")

statefile_start_filename = "state-00050.dtk"
statefile_end_filename = "state-microstructure-zerogroup.dtk"

statefile_start_fullpath = os.path.join(SPOP_FOLDER, statefile_start_filename)
statefile_end_fullpath = os.path.join(SPOP_FOLDER, statefile_end_filename)

simconfig_start_fullpath = os.path.join(SIM_CONFIG_PATH, "config_env_zerogroup_microstructure.json")
simconfig_end_fullpath = os.path.join(SIM_CONFIG_PATH, "config_env_zerogroup_microstructure_final.json")

campaign_fullpath = os.path.join(SIM_CONFIG_PATH, "campaign_seed_infection.json")

with open(simconfig_start_fullpath) as infile:
    params = json.load(infile)["parameters"]

params["Demographics_Filenames"].append(demographics_end_filename)
params["Serialized_Population_Filenames"] = [statefile_end_filename]

with open (simconfig_end_fullpath, 'w') as outfile:
    config = {"parameters": params}
    json.dump(config, outfile, indent=4, sort_keys=True)

# TODO: uncomment these 10 lines when https://github.com/InstituteforDiseaseModeling/emodpy-covid/issues/15 is resolved
from emodpy_covid.microstructure import change_ser_pop

change_ser_pop.change_ser_pop(
    path=statefile_start_fullpath,
    input_demog=demographics_start_fullpath,
    output_demog=demographics_end_fullpath,
    save_file_path=statefile_end_fullpath,
    use_singles_node=True
)

if __name__ == "__main__":
    platform = Platform('COMPS2')

    zerogroup_test_task = EMODTask.from_files(
        eradication_path=ERADICATION_PATH,
        config_path=simconfig_end_fullpath,
        campaign_path=campaign_fullpath,
        demographics_paths=[demographics_end_fullpath]
    )

    statefile_asset = Asset(absolute_path=statefile_end_fullpath)
    zerogroup_test_task.common_assets.add_asset(statefile_asset)

    zerogroup_test_experiment = Experiment.from_task(
        task=zerogroup_test_task,
        name="DTK-Covid microstructure with zerogroup test"
    )

    platform.run_items(zerogroup_test_experiment)
    platform.wait_till_done(zerogroup_test_experiment)

    # TODO: write an analyzer that shows the first few infections all come from a previously infected person
    # NOTE: I turned on the event db, this should be pretty straightforward for the first few timesteps anyway


