#   -*- coding: utf-8 -*-
#
#   This file is part of PyBuilder
#
#   Copyright 2011-2020 PyBuilder Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
from os.path import normcase as nc

from pybuilder.plugins.python.pychecker_plugin import (PycheckerModuleReport,
                                                       PycheckerWarning,
                                                       PycheckerReport,
                                                       parse_pychecker_output)
from test_utils import Mock


class PycheckerWarningTest(unittest.TestCase):
    def test_to_json_dict(self):
        expected = {
            "message": "any message",
            "line_number": 17
        }
        self.assertEqual(
            expected, PycheckerWarning("any message", 17).to_json_dict())


class PycheckerModuleReportTest(unittest.TestCase):
    def test_to_json_dict(self):
        report = PycheckerModuleReport("any.module")
        report.add_warning(PycheckerWarning("warning 1", 1))
        report.add_warning(PycheckerWarning("warning 2", 2))

        expected = {
            "name": "any.module",
            "warnings": [{"message": "warning 1", "line_number": 1},
                         {"message": "warning 2", "line_number": 2}]
        }
        self.assertEqual(expected, report.to_json_dict())


class PycheckerReportTest(unittest.TestCase):
    def test_to_json_dict(self):
        module_report_one = PycheckerModuleReport("any.module")
        module_report_one.add_warning(PycheckerWarning("warning 1", 1))
        module_report_one.add_warning(PycheckerWarning("warning 2", 2))

        module_report_two = PycheckerModuleReport("any.other.module")
        module_report_two.add_warning(PycheckerWarning("warning 1", 3))
        module_report_two.add_warning(PycheckerWarning("warning 2", 4))

        report = PycheckerReport()
        report.add_module_report(module_report_one)
        report.add_module_report(module_report_two)

        expected = {
            "modules": [
                {
                    "name": "any.module",
                    "warnings": [{"message": "warning 1", "line_number": 1},
                                 {"message": "warning 2", "line_number": 2}]
                },
                {
                    "name": "any.other.module",
                    "warnings": [{"message": "warning 1", "line_number": 3},
                                 {"message": "warning 2", "line_number": 4}]
                }
            ]
        }

        self.assertEqual(expected, report.to_json_dict())


class ParsePycheckerOutputTest(unittest.TestCase):
    def test_should_parse_report(self):
        project = Mock()
        project.expand_path.return_value = nc("/path/to")

        warnings = [
            nc("/path/to/package/module_one") + ":2: Sample warning",
            nc("/path/to/package/module_one") + ":4: Another sample warning",
            "",
            nc("/path/to/package/module_two") + ":33: Another sample warning",
            nc("/path/to/package/module_two") + ":332: Yet another sample warning"
        ]

        report = parse_pychecker_output(project, warnings)

        self.assertEqual(2, len(report.module_reports))

        self.assertEqual("package.module_one", report.module_reports[0].name)
        self.assertEqual(2, len(report.module_reports[0].warnings))
        self.assertEqual(
            "Sample warning", report.module_reports[0].warnings[0].message)
        self.assertEqual(2, report.module_reports[0].warnings[0].line_number)
        self.assertEqual("Another sample warning",
                         report.module_reports[0].warnings[1].message)
        self.assertEqual(4, report.module_reports[0].warnings[1].line_number)

        self.assertEqual("package.module_two", report.module_reports[1].name)
        self.assertEqual(2, len(report.module_reports[1].warnings))
        self.assertEqual("Another sample warning",
                         report.module_reports[1].warnings[0].message)
        self.assertEqual(33, report.module_reports[1].warnings[0].line_number)
        self.assertEqual("Yet another sample warning",
                         report.module_reports[1].warnings[1].message)
        self.assertEqual(
            332, report.module_reports[1].warnings[1].line_number)
