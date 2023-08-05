#!/usr/bin/env python

"""
Master tests for FireWorks - generally used to ensure that installation was \
completed properly.
"""
from fireworks import FireWork
from fireworks.core.firework import Workflow
from fireworks.user_objects.firetasks.script_task import ScriptTask

__author__ = "Anubhav Jain"
__copyright__ = "Copyright 2013, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Anubhav Jain"
__email__ = "ajain@lbl.gov"
__date__ = "Jan 9, 2013"

import unittest


class TestImports(unittest.TestCase):
    """
    Make sure that required external libraries can be imported 
    """

    def test_imports(self):
        import yaml
        import pymongo
        import jinja2
        # test that MongoClient is available (newer pymongo)
        from pymongo import MongoClient


class BasicTests(unittest.TestCase):
    """
    Make sure that required external libraries can be imported
    """

    def test_fwconnector(self):
        fw1 = FireWork(ScriptTask.from_str('echo "1"'))
        fw2 = FireWork(ScriptTask.from_str('echo "1"'))

        wf1 = Workflow([fw1, fw2], {fw1.fw_id: fw2.fw_id})
        self.assertEqual(wf1.links, {-1: [-2], -2: []})

        wf2 = Workflow([fw1, fw2], {fw1: fw2})
        self.assertEqual(wf2.links, {-1: [-2], -2: []})

        wf3 = Workflow([fw1, fw2])
        self.assertEqual(wf3.links, {-1: [], -2: []})


if __name__ == "__main__":
    unittest.main()