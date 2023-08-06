# -*- coding: utf-8 -*-

from radish.config import Config
from radish.stepregistry import StepRegistry
from radish.filesystemhelper import FileSystemHelper as fsh
from radish.exceptions import StepDefinitionFileNotFoundError, StepDefinitionNotFoundError
from radish.outlinedstep import OutlinedStep


class Loader(object):
    def __init__(self, features):
        self._features = features

    def load(self):
        self._load_terrain()
        self._load_step_definitions()
        self._load_logger()

    def _load_terrain(self):
        fsh.import_module(Config().basedir, "terrain.py")

    def _load_step_definitions(self):
        if not fsh.locate(Config().basedir, "steps.py"):
            raise StepDefinitionFileNotFoundError(Config().basedir, "steps.py")

        fsh.import_module(Config().basedir, "steps.py")
        self._merge_steps_with_definitions()

    def _load_logger(self):
        if fsh.locate(Config().basedir, "logger.py"):
            fsh.import_module(Config().basedir, "logger.py")

    def _merge_steps_with_definitions(self):
        sr = StepRegistry()
        for feature in self._features:
            for scenario in feature.get_scenarios():
                for step in [s for s in scenario.get_steps() if not isinstance(s, OutlinedStep)]:
                    match, func, metric_indicators = sr.find(step.get_sentence())
                    if match and func:
                        step.set_function(func)
                        step.set_match(match)
                        step.set_metric_indicators(metric_indicators)
                    else:
                        raise StepDefinitionNotFoundError(step.get_sentence(), step.get_filename(), step.get_line_no())
