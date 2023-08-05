#pylint: disable=C0301, C0103, W0212

"""
.. module:: radical.pilot.session
   :platform: Unix
   :synopsis: Implementation of the Session class.

.. moduleauthor:: Ole Weidner <ole.weidner@rutgers.edu>
"""

__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__   = "MIT"

import os 

from radical.pilot.object        import Object
from radical.pilot.unit_manager  import UnitManager
from radical.pilot.pilot_manager import PilotManager
from radical.pilot.credentials   import SSHCredential
from radical.pilot.utils.logger  import logger
from radical.pilot.utils         import DBConnectionInfo
from radical.pilot               import exceptions

from radical.pilot.db            import Session as dbSession
from radical.pilot.db            import DBException

from bson.objectid import ObjectId

# ------------------------------------------------------------------------------
#
class _ProcessRegistry(object):
    """A _ProcessRegistry contains a dictionary of all worker processes 
    that are currently active.
    """
    def __init__(self):
        self._dict = dict()

    def register(self, key, process):
        """Add a new process to the registry.
        """
        if key not in self._dict:
            self._dict[key] = process

    def retrieve(self, key):
        """Retrieve a process from the registry.
        """
        if key not in self._dict:
            return None
        else:
            return self._dict[key]

    def keys(self):
        """List all keys of all process in the registry.
        """
        return self._dict.keys()

    def remove(self, key):
        """Remove a process from the registry.
        """
        if key in self._dict:
            del self._dict[key]

# ------------------------------------------------------------------------------
#
class Session(Object):
    """A Session encapsulates a RADICAL-Pilot instance and is the *root* object
    for all other RADICAL-Pilot objects. 

    A Session holds :class:`radical.pilot.PilotManager` and :class:`radical.pilot.UnitManager`
    instances which in turn hold  :class:`radical.pilot.Pilot` and
    :class:`radical.pilot.ComputeUnit` instances.

    Each Session has a unique identifier :data:`radical.pilot.Session.uid` that can be
    used to re-connect to a RADICAL-Pilot instance in the database.

    **Example**::

        s1 = radical.pilot.Session(database_url=DBURL)
        s2 = radical.pilot.Session(database_url=DBURL, session_uid=s1.uid)

        # s1 and s2 are pointing to the same session
        assert s1.uid == s2.uid
    """

    #---------------------------------------------------------------------------
    #
    def __init__ (self, database_url, database_name="radicalpilot", session_uid=None):
        """Creates a new or reconnects to an exising session.

        If called without a session_uid, a new Session instance is created and 
        stored in the database. If session_uid is set, an existing session is 
        retrieved from the database. 

        **Arguments:**
            * **database_url** (`string`): The MongoDB URL. 

            * **database_name** (`string`): An alternative database name 
              (default: 'radical.pilot').

            * **session_uid** (`string`): If session_uid is set, we try 
              re-connect to an existing session instead of creating a new one.

        **Returns:**
            * A new Session instance.

        **Raises:**
            * :class:`radical.pilot.DatabaseError`

        """

        # Dictionaries holding all manager objects created during the session.
        self._pilot_manager_objects = list()
        self._unit_manager_objects = list()

        # Create a new process registry. All objects belonging to this 
        # session will register their worker processes (if they have any)
        # in this registry. This makes it easier to shut down things in 
        # a more coordinate fashion. 
        self._process_registry = _ProcessRegistry()

        # List of credentials registered with this session.
        self._credentials = []

        try:
            self._database_url  = database_url
            self._database_name = database_name 

            ##########################
            ## CREATE A NEW SESSION ##
            ##########################
            if session_uid is None:

                self._uid = str(ObjectId())
                self._last_reconnect = None

                self._dbs, self._created = dbSession.new(sid=self._uid, 
                                                         db_url=database_url, 
                                                         db_name=database_name)

                logger.info("New Session created%s." % str(self))

            ######################################
            ## RECONNECT TO AN EXISTING SESSION ##
            ######################################
            else:
                # otherwise, we reconnect to an exissting session
                self._dbs, session_info = dbSession.reconnect(sid=session_uid, 
                                                              db_url=database_url, 
                                                              db_name=database_name)

                self._uid = session_uid
                self._created = session_info["created"]
                self._last_reconnect = session_info["last_reconnect"]

                for cred_dict in session_info["credentials"]:
                    self._credentials.append(SSHCredential.from_dict(cred_dict))

                logger.info("Reconnected to existing Session %s." % str(self))

        except DBException, ex:
            raise exceptions.radical.pilotException("Database Error: %s" % ex)  

        self._connection_info = DBConnectionInfo(
            session_id=self._uid,
            dbname=database_name,
            url=database_url
        )

    #---------------------------------------------------------------------------
    #
    def close(self, delete=True):
        """Closes the session.

        All subsequent attempts access objects attached to the session will 
        result in an error. If delete is set to True (default) the session
        data is removed from the database.

        **Arguments:**
            * **delete** (`bool`): Remove session data from MongoDB. 

        **Raises:**
            * :class:`radical.pilot.IncorrectState` if the session is closed
              or doesn't exist. 
        """
        if not self._uid:
            logger.warning("Session object already closed.")

        for pmngr in self._pilot_manager_objects:
            # If delete is true, we also set the terminate flag in the 
            # pilot manager's close method, which causes it to send a 
            # CANCEL request to all pilots.
            pmngr.close(terminate=delete)

        for umngr in self._unit_manager_objects:
            umngr.close()

        if delete is True:
            self._destroy_db_entry()

        logger.info("Closed Session %s." % str(self._uid))
        self._uid = None


    #---------------------------------------------------------------------------
    #
    def as_dict(self):
        """Returns a Python dictionary representation of the object.
        """
        object_dict = {
            "uid": self._uid,
            "created": self._created,
            "last_reconnect": self._last_reconnect,
            "database_name": self._database_name,
            "database_url": self._database_url
        }
        return object_dict

    #---------------------------------------------------------------------------
    #
    def __str__(self):
        """Returns a string representation of the object.
        """
        return str(self.as_dict())

    #---------------------------------------------------------------------------
    #
    @property
    def created(self):
        """Returns the UTC date and time the session was created.
        """
        self._assert_obj_is_valid()
        return self._created

    #---------------------------------------------------------------------------
    #
    @property
    def last_reconnect(self):
        """Returns the most recent UTC date and time the session was
        reconnected to.
        """
        self._assert_obj_is_valid()
        return self._last_reconnect

    #---------------------------------------------------------------------------
    #
    def add_credential(self, credential):
        """Adds a new security credential to the session.
        """
        self._assert_obj_is_valid()

        self._dbs.session_add_credential(credential.as_dict())
        self._credentials.append(credential)
        logger.info("Added credential %s to session %s." % (str(credential), self.uid))

    #---------------------------------------------------------------------------
    #
    @property
    def credentials(self):
        """Returns the security credentials of the session.
        """
        self._assert_obj_is_valid()
        return self._credentials

    #---------------------------------------------------------------------------
    #
    def _destroy_db_entry(self):
        """Terminates the session and removes it from the database.

        All subsequent attempts access objects attached to the session and 
        attempts to re-connect to the session via its uid will result in
        an error.

        **Raises:**
            * :class:`radical.pilot.IncorrectState` if the session is closed
              or doesn't exist. 
        """
        self._assert_obj_is_valid()

        self._dbs.delete()
        logger.info("Deleted session %s from database." % self._uid)
        self._uid = None

    #---------------------------------------------------------------------------
    #
    def list_pilot_managers(self):
        """Lists the unique identifiers of all :class:`radical.pilot.PilotManager` 
        instances associated with this session.

        **Example**::

            s = radical.pilot.Session(database_url=DBURL)
            for pm_uid in s.list_pilot_managers():
                pm = radical.pilot.PilotManager(session=s, pilot_manager_uid=pm_uid) 

        **Returns:**
            * A list of :class:`radical.pilot.PilotManager` uids (`list` oif strings`).

        **Raises:**
            * :class:`radical.pilot.IncorrectState` if the session is closed
              or doesn't exist. 
        """
        self._assert_obj_is_valid()
        return self._dbs.list_pilot_manager_uids()


    # --------------------------------------------------------------------------
    #
    def get_pilot_managers(self, pilot_manager_ids=None) :
        """ Re-connects to and returns one or more existing PilotManager(s).

        **Arguments:**

            * **session** [:class:`radical.pilot.Session`]: 
              The session instance to use.

            * **pilot_manager_uid** [`string`]: 
              The unique identifier of the PilotManager we want 
              to re-connect to.

        **Returns:**

            * One or more new [:class:`radical.pilot.PilotManager`] objects.

        **Raises:**

            * :class:`radical.pilot.radical.pilotException` if a PilotManager with 
              `pilot_manager_uid` doesn't exist in the database.
        """
        self._assert_obj_is_valid()

        return_scalar = False

        if pilot_manager_ids is None:
            pilot_manager_ids = self.list_pilot_managers()

        elif not isinstance(pilot_manager_ids, list):
            pilot_manager_ids = [pilot_manager_ids]
            return_scalar = True

        pilot_manager_objects = []

        for pilot_manager_id in pilot_manager_ids:
            pilot_manager = PilotManager._reconnect(session=self, pilot_manager_id=pilot_manager_id)
            pilot_manager_objects.append(pilot_manager)

            self._pilot_manager_objects.append(pilot_manager)

        if return_scalar is True:
            pilot_manager_objects = pilot_manager_objects[0]

        return pilot_manager_objects

    #---------------------------------------------------------------------------
    #
    def list_unit_managers(self):
        """Lists the unique identifiers of all :class:`radical.pilot.UnitManager` 
        instances associated with this session.

        **Example**::

            s = radical.pilot.Session(database_url=DBURL)
            for pm_uid in s.list_unit_managers():
                pm = radical.pilot.PilotManager(session=s, pilot_manager_uid=pm_uid) 

        **Returns:**
            * A list of :class:`radical.pilot.UnitManager` uids (`list` of `strings`).

        **Raises:**
            * :class:`radical.pilot.IncorrectState` if the session is closed
              or doesn't exist. 
        """
        self._assert_obj_is_valid()
        return self._dbs.list_unit_manager_uids()

    # --------------------------------------------------------------------------
    #
    def get_unit_managers(self, unit_manager_ids=None) :
        """ Re-connects to and returns one or more existing UnitManager(s).

        **Arguments:**

            * **session** [:class:`radical.pilot.Session`]: 
              The session instance to use.

            * **pilot_manager_uid** [`string`]: 
              The unique identifier of the PilotManager we want 
              to re-connect to.

        **Returns:**

            * One or more new [:class:`radical.pilot.PilotManager`] objects.

        **Raises:**

            * :class:`radical.pilot.radical.pilotException` if a PilotManager with 
              `pilot_manager_uid` doesn't exist in the database.
        """
        self._assert_obj_is_valid()

        return_scalar = False
        if unit_manager_ids is None:
            unit_manager_ids = self.list_unit_managers()

        elif not isinstance(unit_manager_ids, list):
            unit_manager_ids = [unit_manager_ids]
            return_scalar = True

        unit_manager_objects = []

        for unit_manager_id in unit_manager_ids:
            unit_manager = UnitManager._reconnect(session=self, unit_manager_id=unit_manager_id)
            unit_manager_objects.append(unit_manager)

            self._unit_manager_objects.append(unit_manager)

        if return_scalar is True:
            unit_manager_objects = unit_manager_objects[0]

        return unit_manager_objects

