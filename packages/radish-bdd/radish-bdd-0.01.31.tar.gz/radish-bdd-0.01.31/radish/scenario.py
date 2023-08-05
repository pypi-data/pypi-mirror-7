# -*- coding: utf-8 -*-

from radish.timetracker import Timetracker
from radish.config import Config
from radish.step import Step
from radish.colorful import colorful


class Scenario(Timetracker):
    def __init__(self, id, feature, sentence, filename, line_no):
        Timetracker.__init__(self)
        self._title = "Scenario"
        self._id = id
        self._feature = feature
        self._sentence = sentence
        self._filename = filename
        self._line_no = line_no
        self._steps = []

    def get_title(self):
        return self._title

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_feature(self):
        return self._feature

    def get_line_no(self):
        return self._line_no

    def get_sentence(self):
        return self._sentence

    def set_sentence(self, sentence):
        self._sentence = sentence

    def get_indentation(self):
        return "  " + " " * len(str(Config().highest_feature_id)) + "  "

    def is_dry_run(self):
        return Config().dry_run

    def get_steps(self):
        return self._steps

    def has_passed(self):
        skipped = True
        for s in self._steps:
            if s.has_passed() is False:
                return False
            elif s.has_passed():
                skipped = False
        return None if skipped else True

    def get_representation(self, ran):
        output = ""
        if ran:
            output = "\n"
        else:
            if not Config().no_indentation:
                output += self.get_indentation()
            if not Config().no_numbers:
                output += colorful.bold_white("%*d. " % (0 if Config().no_indentation else len(str(Config().highest_scenario_id)), self._id))
            if Config().with_section_names:
                output += colorful.bold_white("%s: " % self._title)
            output += colorful.bold_white(self._sentence) + "\n"
        return output


    def append_step(self, step):
        if isinstance(step, Step):
            self._steps.append(step)
