"""
    This example demonstrates how to use dtk_in_process to create transmission blocking
    vaccines at runtime in the DTK. This uses the following new DTK features
    * dtk_in_process
    * Enable_Event_DB enables the DTK to write simulation events to a sqlite file at every timestep
    * TargetDemographic:ExplicitID allows interventions to target individuals by their SUID
"""
# TODO: use an analyzer to confirm that new infections channel is the same as campaign cost channel


# Common python imports
import os

# Code under test imports
from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.emod_task import EMODTask

# Constants

this_folder = os.path.dirname(os.path.realpath(__file__))
ERADICATION_FOLDER = os.path.join(this_folder, "..")
SIM_CONFIG_PATH = os.path.join(this_folder, "Assets")
ERADICATION_PATH = os.path.join(ERADICATION_FOLDER, "Eradication.exe")
PYTHON_PROCESS_FOLDER = os.path.join(this_folder, "Assets")

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS2')

    # in_process_vaccine_task = EMODTask.from_files(
    #     eradication_path=ERADICATION_PATH,
    #     config_path=os.path.join(SIM_CONFIG_PATH, "config.json"),
    #     campaign_path=os.path.join(SIM_CONFIG_PATH, "campaign.json"),
    #     demographics_paths=[]
    # )

    in_process_vaccine_task = EMODTask.from_files(
        eradication_path=ERADICATION_PATH,
        config_path=os.path.join(SIM_CONFIG_PATH, "config.json"),
        campaign_path=os.path.join(SIM_CONFIG_PATH, "campaign.json")
    )

    dtk_in_process_asset = Asset(os.path.join(PYTHON_PROCESS_FOLDER,
                                              "dtk_in_process.py"),
                                 relative_path='python')
    in_process_vaccine_task.common_assets.add_asset(dtk_in_process_asset)

    dtk_post_process_asset = Asset(os.path.join(PYTHON_PROCESS_FOLDER,
                                               "dtk_post_process.py"),
                                  relative_path='python')
    in_process_vaccine_task.common_assets.add_asset(dtk_post_process_asset)

    in_process_vaccine_task.use_embedded_python = True

    experiment = Experiment.from_task(task=in_process_vaccine_task,
                                      name="emodpy test DTK-COVID generic target explicit ID multinode")

    platform.run_items(experiment)
    platform.wait_till_done(experiment)
