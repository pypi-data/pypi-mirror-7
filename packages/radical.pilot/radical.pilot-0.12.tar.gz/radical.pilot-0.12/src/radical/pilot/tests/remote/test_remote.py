""" Test resources
"""

import radical.pilot

import os
import sys
import uuid
import getpass
import unittest

from copy import deepcopy
from radical.pilot.db import Session
from pymongo import MongoClient

# DBURL defines the MongoDB server URL and has the format mongodb://host:port.
# For the installation of a MongoDB server, refer to the MongoDB website:
# http://docs.mongodb.org/manual/installation/
DBURL = os.getenv("RADICAL_PILOT_DBURL")
if DBURL is None:
    print "ERROR: RADICAL_PILOT_DBURL (MongoDB server URL) is not defined."
    sys.exit(1)
    
DBNAME = 'radicalpilot_unittests'

RESCFG = 'https://raw.github.com/radical-cybertools/radical.pilot/master/configs/futuregrid.json'

#-----------------------------------------------------------------------------
#
class TestRemoteSubmission(unittest.TestCase):
    # silence deprecation warnings under py3

    def setUp(self):
        # clean up fragments from previous tests
        client = MongoClient(DBURL)
        client.drop_database(DBNAME)

        self.test_resource = os.getenv('RADICAL_PILOT_TEST_REMOTE_RESOURCE',     "localhost")
        self.test_ssh_uid  = os.getenv('RADICAL_PILOT_TEST_REMOTE_SSH_USER_ID',  None)
        self.test_ssh_key  = os.getenv('RADICAL_PILOT_TEST_REMOTE_SSH_USER_KEY', None)
        self.test_workdir  = os.getenv('RADICAL_PILOT_TEST_REMOTE_WORKDIR',      "/tmp/radical.pilot.sandbox.unittests")
        self.test_cores    = os.getenv('RADICAL_PILOT_TEST_REMOTE_CORES',        "1")
        self.test_num_cus  = os.getenv('RADICAL_PILOT_TEST_REMOTE_NUM_CUS',      "2")
        self.test_timeout  = os.getenv('RADICAL_PILOT_TEST_TIMEOUT',             "5")

    def tearDown(self):
        # clean up after ourselves 
        client = MongoClient(DBURL)
        client.drop_database(DBNAME)

    def failUnless(self, expr):
        # St00pid speling.
        return self.assertTrue(expr)

    def failIf(self, expr):
        # St00pid speling.
        return self.assertFalse(expr)

    #-------------------------------------------------------------------------
    #
    def test__remote_simple_submission(self):
        """ Test simple remote submission with one pilot.
        """
        session = radical.pilot.Session(database_url=DBURL, database_name=DBNAME)
        cred = radical.pilot.SSHCredential()
        cred.user_id  = self.test_ssh_uid
        cred.user_key = self.test_ssh_key

        session.add_credential(cred)

        pm = radical.pilot.PilotManager(session=session, resource_configurations=RESCFG)

        cpd = radical.pilot.ComputePilotDescription()
        cpd.resource = self.test_resource
        cpd.cores = self.test_cores
        cpd.runtime = 5
        cpd.sandbox = self.test_workdir

        pilot = pm.submit_pilots(pilot_descriptions=cpd)

        um = radical.pilot.UnitManager(session=session, scheduler='round_robin')
        um.add_pilots(pilot)

        cudescs = []
        for _ in range(0,int(self.test_num_cus)):
            cudesc = radical.pilot.ComputeUnitDescription()
            cudesc.cores = 1
            cudesc.executable = "/bin/sleep"
            cudesc.arguments = ['10']
            cudescs.append(cudesc)

        cus = um.submit_units(cudescs)

        for cu in cus:
            assert cu is not None
            assert cu.start_time is None
            assert cu.stop_time is None

        um.wait_units(state=[radical.pilot.states.DONE, radical.pilot.states.FAILED], timeout=self.test_timeout)

        for cu in cus:
            assert cu.state == radical.pilot.states.DONE
            assert cu.stop_time is not None

        pm.cancel_pilots()

        session.close()

    #-------------------------------------------------------------------------
    #
    def test__remote_pilot_wait(self):
        """ Test if we can wait for different pilot states. 
        """
        session = radical.pilot.Session(database_url=DBURL, database_name=DBNAME)
        cred = radical.pilot.SSHCredential()
        cred.user_id  = self.test_ssh_uid
        cred.user_key = self.test_ssh_key

        session.add_credential(cred)

        pm = radical.pilot.PilotManager(session=session, resource_configurations=RESCFG)

        cpd = radical.pilot.ComputePilotDescription()
        cpd.resource          = self.test_resource
        cpd.cores             = self.test_cores
        cpd.runtime           = 2
        cpd.sandbox           = self.test_workdir 

        pilot = pm.submit_pilots(pilot_descriptions=cpd)

        assert pilot is not None
        #assert cu.start_time is None
        #assert cu.start_time is None

        pilot.wait(radical.pilot.states.ACTIVE, timeout=5.0*60)
        assert pilot.state == radical.pilot.states.ACTIVE
        assert pilot.start_time is not None
        assert pilot.submission_time is not None


        # the pilot should finish after it has reached run_time
        pilot.wait(radical.pilot.states.DONE, timeout=5.0*60)
        assert pilot.state == radical.pilot.states.DONE
        assert pilot.stop_time is not None

        session.close()

    #-------------------------------------------------------------------------
    #
    def test__remote_pilot_cancel(self):
        """ Test if we can cancel a pilot. 
        """
        session = radical.pilot.Session(database_url=DBURL, database_name=DBNAME)
        cred = radical.pilot.SSHCredential()
        cred.user_id  = self.test_ssh_uid
        cred.user_key = self.test_ssh_key

        session.add_credential(cred)

        pm = radical.pilot.PilotManager(session=session, resource_configurations=RESCFG)

        cpd = radical.pilot.ComputePilotDescription()
        cpd.resource          = self.test_resource
        cpd.cores             = self.test_cores
        cpd.runtime           = 2
        cpd.sandbox           = self.test_workdir 

        pilot = pm.submit_pilots(pilot_descriptions=cpd)

        assert pilot is not None
        #assert cu.start_time is None
        #assert cu.start_time is None

        pilot.wait(radical.pilot.states.ACTIVE)
        assert pilot.state == radical.pilot.states.ACTIVE, "Expected state 'ACTIVE' but got %s" % pilot.state
        assert pilot.submission_time is not None
        assert pilot.start_time is not None

        # the pilot should finish after it has reached run_time
        pilot.cancel()

        pilot.wait(radical.pilot.states.CANCELED, timeout=5.0*60)
        assert pilot.state == radical.pilot.states.CANCELED
        assert pilot.stop_time is not None

        session.close()

