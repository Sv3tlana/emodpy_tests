# Common python imports
import os
import json

# Code under test imports
from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.emod_task import EMODTask
import emodpy_covid

# Constants

this_folder = os.path.dirname(os.path.realpath(__file__))
ERADICATION_FOLDER = os.path.join(this_folder, "..")
SIM_CONFIG_PATH = os.path.join(this_folder, "Assets")
ERADICATION_PATH = os.path.join(ERADICATION_FOLDER, "Eradication.exe")
PYTHON_PROCESS_FOLDER = os.path.join(this_folder, "Assets")

class InProcTraceDemo():
    def __init__(self, path_to_eradication):
        self.eradication_path = path_to_eradication
        self.demograpahics_files = []
        self.config_params = []
        self.py_pre_processing = None
        self.py_in_processing = None
        self.py_post_processing = None

    def build_covid_assets(self, demographics_filenames=None):
        if not demographics_filenames:
            self.demograpahics_files = [emodpy_covid.get_covid_demographics()]
        else:
            for filename in demographics_filenames:
                self.demograpahics_files.append(json.load(open(filename)))

        self.config_params = emodpy_covid.get_covid_config_default(self.eradication_path)
        self.in_process_script = emodpy_covid.embedded_python.get_contact_trace_in_proc(
            start_day = 15,
            trace_probability = 0.8)
        pass

    def write_covid_assets(self,
                           config_name="config.json",
                           demographics_filenames=["demographics.json"]
                           ):
        if len(demographics_filenames) != len(self.demograpahics_files):
            raise ValueError("Mismatch: number of demographics filenames should equal number of demogrpahics files.")
        config = {
            'parameters': self.config_params,
            'provenance': emodpy_covid.get_provenance_dict
        }
        with open(config_name, "w") as outfile:
            json.dump(config, outfile, indent=4, sort_keys=True)

        for x in range(len(demographics_filenames)):
            with open(demographics_filenames[x], "w") as demog_file:
                json.dump(self.demograpahics_files[x], outfile, indent=4, sort_keys=True)

        embedded_py_scripts = [self.py_pre_processing, self.py_in_processing, self.py_post_processing]
        script_names = ["dtk_pre_process.py", "dtk_in_process.py", "dtk_post_process.py"]
        expected_scripts = []
        for x in range(len(embedded_py_scripts)):
            if embedded_py_scripts[x]:
                with open(script_names[x], "w") as outfile:
                    outfile.write(embedded_py_scripts[x])
                    expected_scripts.append(script_names[x])

        return config_name, demographics_filenames, expected_scripts


    def build_simulation_task(self, path_to_eradication, config_filename,
                              demographics_filenames, embedded_py_scripts):
        in_process_vaccine_task = EMODTask.from_files(
        eradication_path=path_to_eradication,
        config_path=config_filename,
        campaign_path=os.path.join(SIM_CONFIG_PATH, "campaign.json")
    )
        for d in demographics_filenames:
            tmp_demographics_asset = Asset(
                d
            )
            in_process_vaccine_task.common_assets.add_asset(tmp_demographics_asset)
        for s in embedded_scriptnames:
            tmp_processing_asset = Asset(
                s, relative_path='python')
            in_process_vaccine_task.common_assets.add_asset(tmp_processing_asset)

        in_process_vaccine_task.use_embedded_python = True
        return in_process_vaccine_task

if __name__ == "__main__":
    # Create the platform
    platform = Platform('COMPS2')
    erad_path = os.path.join("MyAssets", "Eradication.exe")
    demo = InProcTraceDemo(path_to_eradication=erad_path)
    demo.build_covid_assets()
    config_filename, demographics_filenames, embedded_scriptnames = demo.write_covid_assets()
    in_process_vaccine_task = demo.build_simulation_task(
        path_to_eradication=erad_path,
        config_filename=config_filename,
        demographics_filenames=demographics_filenames,
        embedded_py_scripts=embedded_scriptnames
    )

    experiment = Experiment.from_task(task=in_process_vaccine_task,
                                      name="emodpy test DTK-COVID generic target explicit ID multinode")

    platform.run_items(experiment)
    