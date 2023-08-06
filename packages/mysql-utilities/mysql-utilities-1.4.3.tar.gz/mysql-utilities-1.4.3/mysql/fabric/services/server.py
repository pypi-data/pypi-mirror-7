#
# Copyright (c) 2013,2014, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
"""This module provides the necessary interfaces for performing administrative
tasks on groups and servers, specifically MySQL Servers.

It is possible to add, update and remove a group. One cannot, however, remove
a group if there are associated servers. It is possible to add a server to a
group and remove a server from a group. Search functions are also provided so
that one may look up groups and servers. Given a server's address, one may
also find out the server's uuid if the server is alive and kicking.

When a group is created though, it is inactive which means that the failure
detector will not check if its servers are alive. To start up the failure
detector, one needs to explicitly activate it per group. A server may have
one of the following statuses:

- PRIMARY - This is set when the server may accept both reads and writes
  operations.
- SECONDARY - This is set when the server may accept only read operations.
- SPARE - This is set when users want to have server that is kept in sync
  but does not accept neither reads or writes operations.
- FAULTY - This is set by the failure detector and indicates that a server
  is not reachable.

Find in what follows the possible state transitions:

.. graphviz::

   digraph state_transition {
    rankdir=LR;
    size="8,5"

    node [shape = circle]; Primary;
    node [shape = circle]; Secondary;
    node [shape = circle]; Spare;
    node [shape = circle]; Faulty;

    Primary   -> Secondary [ label = "demote" ];
    Primary   -> Faulty [ label = "failure" ];
    Secondary -> Primary [ label = "promote" ];
    Secondary -> Spare [ label = "set_status" ];
    Secondary -> Faulty [ label = "failure" ];
    Spare     -> Primary [ label = "promote" ];
    Spare     -> Secondary [ label = "set_status" ];
    Spare     -> Faulty [ label = "failure" ];
    Faulty    -> Spare [ label = "set_status" ];
  }

It is worth noticing that this module only provides functions for performing
basic administrative tasks, provisioning and high-availability functions are
provided elsewhere.
"""
import logging
import uuid as _uuid

import mysql.fabric.services.utils as _utils

from mysql.fabric import (
    backup as _backup,
    events as _events,
    server as _server,
    errors as _errors,
    failure_detector as _detector,
    group_replication as _group_replication,
    sharding as _sharding,
    server_utils as _server_utils,
)

from mysql.fabric.command import (
    ProcedureGroup,
    Command,
)

from mysql.fabric.utils import (
    get_time,
)

_LOGGER = logging.getLogger(__name__)

SERVER_NOT_FOUND = "Server with UUID %s not found."
MYSQLDUMP_NOT_FOUND = "Unable to find MySQLDump in location %s"
MYSQLCLIENT_NOT_FOUND = "Unable to find MySQL Client in location %s"

class GroupLookups(Command):
    """Return information on existing group(s).
    """
    group_name = "group"
    command_name = "lookup_groups"

    def execute(self, group_id=None):
        """Return information on existing group(s).

        :param group_id: None if one wants to list the existing groups or
                         group's id if one wants information on a group.
        :return: List with {"group_id" : group_id, "failure_detector": ON/OFF,
                 "description" : description}.
        """
        return Command.generate_output_pattern(
            _lookup_groups, group_id)

CREATE_GROUP = _events.Event()
class GroupCreate(ProcedureGroup):
    """Create a group.
    """
    group_name = "group"
    command_name = "create"

    def execute(self, group_id, description=None, synchronous=True):
        """Create a group.

        :param group_id: Group's id.
        :param description: Group's description.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(
            CREATE_GROUP, self.get_lockable_objects(), group_id, description
        )
        return self.wait_for_procedures(procedures, synchronous)

UPDATE_GROUP = _events.Event()
class GroupDescription(ProcedureGroup):
    """Update group's description.
    """
    group_name = "group"
    command_name = "description"

    def execute(self, group_id, description=None, synchronous=True):
        """Update group's description.

        :param group_id: Group's id.
        :param description: Group's description.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(
            UPDATE_GROUP, self.get_lockable_objects(), group_id, description
        )
        return self.wait_for_procedures(procedures, synchronous)

DESTROY_GROUP = _events.Event()
class DestroyGroup(ProcedureGroup):
    """Remove a group.
    """
    group_name = "group"
    command_name = "destroy"

    def execute(self, group_id, force=False, synchronous=True):
        """Remove a group.

        :param group_id: Group's id.
        :param force: If the group is not empty, remove it serves.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(
            DESTROY_GROUP, self.get_lockable_objects(), group_id, force
        )
        return self.wait_for_procedures(procedures, synchronous)

class ServerLookups(Command):
    """Return information on existing server(s) in a group.
    """
    group_name = "group"
    command_name = "lookup_servers"

    def execute(self, group_id, server_id=None, status=None, mode=None):
        """Return information on existing server(s) in a group.

        :param group_id: Group's id.
        :param uuid: None if one wants to list the existing servers
                     in a group or server's id if one wants information
                     on a server in a group.
        :server_id type: Servers's UUID or HOST:PORT.
        :param status: Server's status one is searching for.
        :param mode: Server's mode one is searching for.
        :return: Information on servers.
        :rtype: List with [uuid, address, status, mode, weight]
        """
        return Command.generate_output_pattern(
            _lookup_servers, group_id, server_id, status, mode
        )

class ServerUuid(Command):
    """Return server's uuid.
    """
    group_name = "server"
    command_name = "lookup_uuid"

    def execute(self, address, timeout=5):
        """Return server's UUID.

        :param address: Server's address.
        :param timeout: Time in seconds after which an error is reported
                        if the UUID is not retrieved.
        :return: UUID.
        """
        return Command.generate_output_pattern(_lookup_uuid, address, timeout)

ADD_SERVER = _events.Event()
class ServerAdd(ProcedureGroup):
    """Add a server into group.

    If users just want to update the state store and skip provisioning steps
    such as configuring replication, the update_only parameter must be set to
    true.

    Note that the current implementation has a simple provisioning step that
    makes the server point to the master if there is any.
    """
    group_name = "group"
    command_name = "add"

    def execute(self, group_id, address, timeout=5, update_only=False,
                synchronous=True):
        """Add a server into a group.

        :param group_id: Group's id.
        :param address: Server's address.
        :param timeout: Time in seconds after which an error is reported
                        if one cannot access the server.
        :update_only: Only update the state store and skip provisioning.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(ADD_SERVER, self.get_lockable_objects(),
            group_id, address, timeout, update_only
        )
        return self.wait_for_procedures(procedures, synchronous)

REMOVE_SERVER = _events.Event()
class ServerRemove(ProcedureGroup):
    """Remove a server from a group.
    """
    group_name = "group"
    command_name = "remove"

    def execute(self, group_id, server_id, synchronous=True):
        """Remove a server from a group.

        :param group_id: Group's id.
        :param server_id: Servers's UUID or HOST:PORT.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(REMOVE_SERVER, self.get_lockable_objects(),
            group_id, server_id
        )
        return self.wait_for_procedures(procedures, synchronous)

ACTIVATE_GROUP = _events.Event()
class ActivateGroup(ProcedureGroup):
    """Activate failure detector for server(s) in a group.

    By default the failure detector is disabled.
    """
    group_name = "group"
    command_name = "activate"

    def execute(self, group_id, synchronous=True):
        """Activate a group.

        :param group_id: Group's id.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(
            ACTIVATE_GROUP, self.get_lockable_objects(), group_id
        )
        return self.wait_for_procedures(procedures, synchronous)

DEACTIVATE_GROUP = _events.Event()
class DeactivateGroup(ProcedureGroup):
    """Deactivate failure detector for server(s) in a group.

    By default the failure detector is disabled.
    """
    group_name = "group"
    command_name = "deactivate"

    def execute(self, group_id, synchronous=True):
        """Deactivate group.

        :param group_id: Group's id.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(
            DEACTIVATE_GROUP, self.get_lockable_objects(), group_id
        )
        return self.wait_for_procedures(procedures, synchronous)

class DumpServers(Command):
    """Return information about servers.

    The servers might belong to any group that matches any of the provided
    patterns, or all servers if no patterns are provided.
    """
    group_name = "dump"
    command_name = "servers"

    def execute(self, connector_version=None, patterns=""):
        """Return information about all servers.

        :param connector_version: The connectors version of the data.
        :param patterns: group pattern.
        """
        return _server.MySQLServer.dump_servers(connector_version, patterns)

SET_SERVER_STATUS = _events.Event()
class SetServerStatus(ProcedureGroup):
    """Set a server's status.

    Any server added into a group has to be alive and kicking and its status
    is automatically set to SECONDARY. If the failure detector is activate
    and the server is not reachable, it is automatically set to FAULTY.

    Users can also manually change the server's status. Usually, a user may
    change a slave's mode to SPARE to avoid write and read access and
    guarantee that it is not choosen when a failover or swithover routine is
    executed.

    By default replication is automatically configured when a server has its
    status changed. In order to skip this, users must set the update_only
    parameter to true. If done so, only the state store will be updated with
    information on the new status.
    """
    group_name = "server"
    command_name = "set_status"

    def execute(self, server_id, status, update_only=False, synchronous=True):
        """Set a server's status.

        :param server_id: Servers's UUID or HOST:PORT.
        :param status: Server's status.
        :update_only: Only update the state store and skip provisioning.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        """
        procedures = _events.trigger(
            SET_SERVER_STATUS, self.get_lockable_objects(), server_id, status,
            update_only
        )
        return self.wait_for_procedures(procedures, synchronous)

SET_SERVER_WEIGHT = _events.Event()
class SetServerWeight(ProcedureGroup):
    """Set a server's weight.

    The weight determines the likelihood of a server being choseen by a
    connector to process transactions. For example, a server whose weight
    is 2.0 may receive 2 times more requests than a server whose weight is
    1.0.
    """
    group_name = "server"
    command_name = "set_weight"

    def execute(self, server_id, weight, synchronous=True):
        """Set a server's weight.

        :param server_id: Servers's UUID or HOST:PORT.
        :param weight: Server's weight.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        """
        procedures = _events.trigger(
            SET_SERVER_WEIGHT, self.get_lockable_objects(), server_id, weight
        )
        return self.wait_for_procedures(procedures, synchronous)

SET_SERVER_MODE = _events.Event()
class SetServerMode(ProcedureGroup):
    """Set a server's mode.

    The mode determines whether a server can process read-only, read-write
    or both transaction types.
    """
    group_name = "server"
    command_name = "set_mode"

    def execute(self, server_id, mode, synchronous=True):
        """Set a server's mode.

        :param server_id: Servers's UUID or HOST:PORT.
        :param weight: Server's weight.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        """
        procedures = _events.trigger(
            SET_SERVER_MODE, self.get_lockable_objects(), server_id, mode
        )
        return self.wait_for_procedures(procedures, synchronous)

BACKUP_SERVER = _events.Event("BACKUP_SERVER")
RESTORE_SERVER = _events.Event("RESTORE_SERVER")
class CloneServer(ProcedureGroup):
    """Clone the objects of a given server into a destination server.
    """
    group_name = "server"
    command_name = "clone"

    def execute(self, group_id, destn_address, server_uuid=None,
                synchronous=True):
        """Clone the objects of a given server into a destination server.

        :param group_id: The ID of the source group.
        :param destn_address: The address of the MySQL Server to which
            the clone needs to happen.
        :param server_uuid: The UUID of the source MySQL Server.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        """
        #If the destination server is already part of a Fabric Group, raise
        #an error
        if destn_address:
            destn_server_uuid = _server.MySQLServer.\
                discover_uuid(destn_address)
            destn_server = _server.MySQLServer.fetch(destn_server_uuid)
            #we should check for both the presence of the server object
            #and its associated group ID. Checking its association with
            #a group ID would verify that a server that is part of Fabric
            #but is not part of a group can also be cloned into.
            if destn_server and destn_server.group_id:
                raise _errors.ServerError("The Destination server is already "\
                    "part of Group (%s)" % (destn_server.group_id,))

        config_file = self.config.config_file if self.config.config_file else ""

        mysqldump_binary = _utils.read_config_value(
                                self.config,
                                'sharding',
                                'mysqldump_program'
                            )
        mysqlclient_binary = _utils.read_config_value(
                                self.config,
                                'sharding',
                                'mysqlclient_program'
                            )

        if not _utils.is_valid_binary(mysqldump_binary):
            raise _errors.ServerError(MYSQLDUMP_NOT_FOUND % mysqldump_binary)

        if not _utils.is_valid_binary(mysqlclient_binary):
            raise _errors.ServerError(MYSQLCLIENT_NOT_FOUND % mysqlclient_binary)

        if server_uuid:
            server = _server.MySQLServer.fetch(server_uuid)
            if group_id != server.group_id:
                raise _errors.ServerError("The server %s was not found in "\
                                          "group %s" % (server_uuid, group_id, ))
        elif not server_uuid:
            group = _server.Group.fetch(group_id)
            server = _utils.fetch_backup_server(group)
            server_uuid = str(server.uuid)

        host, port = _server_utils.split_host_port(
                                destn_address,
                                _backup.MySQLDump.MYSQL_DEFAULT_PORT
                            )

        procedures = _events.trigger(
            BACKUP_SERVER,
            self.get_lockable_objects(),
            server_uuid,
            host,
            port,
            mysqldump_binary,
            mysqlclient_binary,
            config_file
        )
        return self.wait_for_procedures(procedures, synchronous)

def _lookup_groups(group_id=None):
    """Return a list of existing group(s).
    """
    info = []
    if group_id is None:
        for group_id in _server.Group.groups():
            _group_information(_server.Group.fetch(group_id[0]), info)
    else:
        group = _retrieve_group(group_id)
        _group_information(group, info)
    return info

def _group_information(group, info):
    """Get information on group and append it into to a list.
    """
    master = str(group.master) if group.master else ""
    info.append({
        "group_id" : group.group_id,
        "description" : group.description or "",
        "failure_detector" : True if group.status else False,
        "master_uuid" : master
    })

@_events.on_event(CREATE_GROUP)
def _create_group(group_id, description):
    """Create a group.
    """
    _check_group_exists(group_id)

    group = _server.Group(group_id=group_id, description=description,
                          status=_server.Group.INACTIVE)
    _server.Group.add(group)
    _LOGGER.debug("Added group (%s).", group)

@_events.on_event(ACTIVATE_GROUP)
def _activate_group(group_id):
    """Activate a group.
    """
    group = _retrieve_group(group_id)
    group.status = _server.Group.ACTIVE

    _detector.FailureDetector.register_group(group_id)
    _LOGGER.debug("Group (%s) is active.", group)

@_events.on_event(DEACTIVATE_GROUP)
def _deactivate_group(group_id):
    """Deactivate a group.
    """
    group = _retrieve_group(group_id)
    group.status = _server.Group.INACTIVE
    _detector.FailureDetector.unregister_group(group_id)
    _LOGGER.debug("Group (%s) is active.", str(group))

@_events.on_event(UPDATE_GROUP)
def _update_group_description(group_id, description):
    """Update a group description.
    """
    group = _retrieve_group(group_id)
    group.description = description
    _LOGGER.debug("Updated group (%s).", group)

@_events.on_event(DESTROY_GROUP)
def _destroy_group(group_id, force):
    """Destroy a group.
    """
    group = _retrieve_group(group_id)

    _check_shard_exists(group_id)

    servers = group.servers()
    if servers and force:
        for server in servers:
            _server.MySQLServer.remove(server)
    elif servers:
        raise _errors.GroupError("Group (%s) is not empty." % (group_id, ))

    _detector.FailureDetector.unregister_group(group_id)
    _server.Group.remove(group)
    _LOGGER.debug("Removed group (%s).", group)

def _lookup_servers(group_id, server_id=None, status=None, mode=None):
    """Return existing servers in a group or information on a server.
    """
    group = _retrieve_group(group_id)

    status = _retrieve_server_status(status) if status is not None else None
    if status is None:
        status = _server.MySQLServer.SERVER_STATUS
    else:
        status = [status]

    mode = _retrieve_server_mode(mode) if mode is not None else None
    if mode is None:
        mode = _server.MySQLServer.SERVER_MODE
    else:
        mode = [mode]

    info = []
    if server_id is None:
        for server in group.servers():
            if server.status in status and server.mode in mode:
                _server_information(server, info)
    else:
        server = _retrieve_server(server_id, group_id)
        _server_information(server, info)

    return info

def _server_information(server, info):
    """Get information on server and append it into to a list.
    """
    info.append({
        "server_uuid" : str(server.uuid),
        "address" : server.address,
        "status" : server.status,
        "mode" : server.mode,
        "weight" : server.weight,
    })

def _lookup_uuid(address, timeout):
    """Return server's uuid.
    """
    try:
        return _server.MySQLServer.discover_uuid(
            address=address, connection_timeout=timeout
        )
    except _errors.DatabaseError:
        raise _errors.ServerError("Error accessing server (%s)." % (address, ))

@_events.on_event(ADD_SERVER)
def _add_server(group_id, address, timeout, update_only):
    """Add a server into a group.
    """
    group = _retrieve_group(group_id)
    uuid = _lookup_uuid(address, timeout)
    _check_server_exists(uuid)
    server = _server.MySQLServer(uuid=_uuid.UUID(uuid), address=address)

    # Check if the server fulfils the necessary requirements to become
    # a member.
    _check_requirements(server)

    # Add server to the state store.
    _server.MySQLServer.add(server)

    # Add server as a member in the group.
    server.group_id = group_id

    if not update_only:
        # Configure the server as a slave if there is a master.
        _configure_as_slave(group, server)

    _LOGGER.debug("Added server (%s) to group (%s).", server, group)

@_events.on_event(REMOVE_SERVER)
def _remove_server(group_id, server_id):
    """Remove a server from a group.
    """
    group = _retrieve_group(group_id)
    server = _retrieve_server(server_id, group_id)

    if group.master == server.uuid:
        raise _errors.ServerError(
            "Cannot remove server (%s), which is master in group (%s). "
            "Please, demote it first." % (server.uuid, group_id)
        )

    _server.MySQLServer.remove(server)
    server.disconnect()
    _server.ConnectionPool().purge_connections(server.uuid)

@_events.on_event(SET_SERVER_STATUS)
def _set_server_status(server_id, status, update_only):
    """Set a server's status.
    """
    status = _retrieve_server_status(status)
    server = _retrieve_server(server_id)

    if status == _server.MySQLServer.PRIMARY:
        _set_server_status_primary(server, update_only)
    elif status == _server.MySQLServer.FAULTY:
        _set_server_status_faulty(server, update_only)
    elif status == _server.MySQLServer.SECONDARY:
        _set_server_status_secondary(server, update_only)
    elif status == _server.MySQLServer.SPARE:
        _set_server_status_spare(server, update_only)

def _retrieve_server_status(status):
    """Check whether the server's status is valid or not and
    if an integer was provided retrieve the correspondent
    string.
    """
    valid = False
    try:
        idx = int(status)
        try:
            status = _server.MySQLServer.get_status(idx)
            valid = True
        except IndexError:
            pass
    except ValueError:
        try:
            status = str(status).upper()
            _server.MySQLServer.get_status_idx(status)
            valid = True
        except ValueError:
            pass

    if not valid:
        values = [ str((_server.MySQLServer.get_status_idx(value), value))
                   for value in _server.MySQLServer.SERVER_STATUS ]
        raise _errors.ServerError("Trying to use an invalid status (%s). "
            "Possible values are %s." % (status, ", ".join(values))
        )

    return status

def _set_server_status_primary(server, update_only):
    """Set server's status to primary.
    """
    raise _errors.ServerError(
        "If you want to make a server (%s) primary, please, use the "
        "group.promote function." % (server.uuid, )
    )

def _set_server_status_faulty(server, update_only):
    raise _errors.ServerError(
        "If you want to set a server (%s) to faulty, please, use the "
        "threat.report_faulty interface." % (server.uuid, )
    )

def _set_server_status_secondary(server, update_only):
    """Set server's status to secondary.
    """
    allowed_status = [_server.MySQLServer.SPARE]
    status = _server.MySQLServer.SECONDARY
    mode = _server.MySQLServer.READ_ONLY
    _do_set_status(server, allowed_status, status, mode, update_only)

def _set_server_status_spare(server, update_only):
    """Set server's status to spare.
    """
    allowed_status = [
        _server.MySQLServer.SECONDARY, _server.MySQLServer.FAULTY
    ]
    status = _server.MySQLServer.SPARE
    mode = _server.MySQLServer.OFFLINE
    previous_status = server.status
    _do_set_status(server, allowed_status, status, mode, update_only)

    if previous_status == _server.MySQLServer.FAULTY:
        # Check whether the server is really alive or not.
        _check_requirements(server)

        # Configure replication
        if not update_only:
             group = _server.Group.fetch(server.group_id)
             _configure_as_slave(group, server)

def _do_set_status(server, allowed_status, status, mode, update_only):
    """Set server's status.
    """
    allowed_transition = server.status in allowed_status
    previous_status = server.status
    if allowed_transition:
        server.status = status
        server.mode = mode
    else:
        raise _errors.ServerError(
            "Cannot change server's (%s) status from (%s) to (%s)." %
            (str(server.uuid), server.status, status)
        )

    _LOGGER.debug(
        "Changed server's status (%s) from (%s) to (%s). Update-only "
        "state store parameter is (%s).", str(server.uuid), previous_status,
        server.status, update_only
    )

@_events.on_event(SET_SERVER_WEIGHT)
def _set_server_weight(server_id, weight):
    """Set server's weight.
    """
    server = _retrieve_server(server_id)

    try:
        weight = float(weight)
    except ValueError:
        raise _errors.ServerError("Value (%s) must be a float." % (weight, ))

    if weight <= 0.0:
        raise _errors.ServerError(
            "Cannot set the server's weight (%s) to a value lower "
            "than or equal to 0.0" % (weight, )
        )
    server.weight = weight

@_events.on_event(SET_SERVER_MODE)
def _set_server_mode(server_id, mode):
    """Set server's mode.
    """
    mode = _retrieve_server_mode(mode)
    server = _retrieve_server(server_id)

    if server.status == _server.MySQLServer.PRIMARY:
        _set_server_mode_primary(server, mode)
    elif server.status == _server.MySQLServer.SECONDARY:
        _set_server_mode_secondary(server, mode)
    elif server.status == _server.MySQLServer.SPARE:
        _set_server_mode_spare(server, mode)
    elif server.status == _server.MySQLServer.FAULTY:
        _set_server_mode_faulty(server, mode)

@_events.on_event(BACKUP_SERVER)
def _backup_server(source_uuid, host, port, mysqldump_binary,
                   mysqlclient_binary, config_file):
    """Backup the source server, given by the source_uuid.

    :param source_uuid: The UUID of the source server.
    :param host: The hostname of the destination server.
    :param port: The port number of the destination server.
    :param mysqldump_binary: The MySQL Dump Binary path.
    :param mysqlclient_binary: The MySQL Client Binary path.
    :param config_file: The complete path to the fabric configuration
        file.
    """
    source_server = _server.MySQLServer.fetch(source_uuid)
    #Do the backup of the group hosting the source shard.
    backup_image = _backup.MySQLDump.backup(
                        source_server,
                        config_file,
                        mysqldump_binary
                    )
    _LOGGER.debug("Done with backup of server with uuid = %s.", source_uuid)
    procedures = _events.trigger_within_procedure(
        RESTORE_SERVER,
        source_uuid,
        host,
        port,
        backup_image.path,
        mysqlclient_binary,
        config_file
    )

@_events.on_event(RESTORE_SERVER)
def _restore_server(source_uuid, host, port, backup_image, mysqlclient_binary,
                    config_file):
    """Restore the backup on the destination Server.

    :param source_uuid: The UUID of the source server.
    :param host: The hostname of the destination server.
    :param port: The port number of the destination server.
    :param userid: The User Name to be used to connect to the destn server.
    :param passwd: The password to be used to connect to the destn server.
    :param mysqldump_binary: The MySQL Dump Binary path.
    :param mysqlclient_binary: The MySQL Client Binary path.
    :param config_file: The complete path to the fabric configuration
        file.
    """
    source_server = _server.MySQLServer.fetch(source_uuid)
    if not source_server:
        raise _errors.ServerError(SERVER_NOT_FOUND % source_uuid)
    #Build a backup image that will be used for restoring
    bk_img = _backup.BackupImage(backup_image)
    _backup.MySQLDump.restore_server(
        host,
        port,
        source_server.USER,
        source_server.PASSWD,
        bk_img,
        config_file,
        mysqlclient_binary
    )
    _LOGGER.debug("Done with restore of server with host = %s, port = %s" %\
                  (host, port,))

def _retrieve_server_mode(mode):
    """Check whether the server's mode is valid or not and if an integer was
    provided retrieve the correspondent string.
    """
    valid = False
    try:
        idx = int(mode)
        try:
            mode = _server.MySQLServer.get_mode(idx)
            valid = True
        except IndexError:
            pass
    except ValueError:
        try:
            mode = str(mode).upper()
            _server.MySQLServer.get_mode_idx(mode)
            valid = True
        except ValueError:
            pass

    if not valid:
        values = [ str((_server.MySQLServer.get_mode_idx(value), value))
                   for value in _server.MySQLServer.SERVER_MODE ]
        raise _errors.ServerError("Trying to use an invalid mode (%s). "
            "Possible values are: %s." % (mode, ", ".join(values))
        )

    return mode

def _set_server_mode_primary(server, mode):
    """Set server's mode when it is a primary.
    """
    allowed_mode = \
        (_server.MySQLServer.WRITE_ONLY, _server.MySQLServer.READ_WRITE)
    _do_set_server_mode(server, mode, allowed_mode)

def _set_server_mode_secondary(server, mode):
    """Set server's mode when it is a secondary.
    """
    allowed_mode = \
        (_server.MySQLServer.OFFLINE, _server.MySQLServer.READ_ONLY)
    _do_set_server_mode(server, mode, allowed_mode)

def _set_server_mode_spare(server, mode):
    """Set server's mode when it is a spare.
    """
    allowed_mode = \
        (_server.MySQLServer.OFFLINE, _server.MySQLServer.READ_ONLY)
    _do_set_server_mode(server, mode, allowed_mode)

def _set_server_mode_faulty(server, mode):
    """Set server's mode when it is a faulty.
    """
    allowed_mode = ()
    _do_set_server_mode(server, mode, allowed_mode)

def _do_set_server_mode(server, mode, allowed_mode):
    """Set server's mode.
    """
    if mode not in allowed_mode:
        raise _errors.ServerError(
            "Cannot set mode to (%s) when the server's (%s) status is (%s)."
            % (mode, server.uuid, server.status)
        )
    server.mode = mode

def _retrieve_server(server_id, group_id=None):
    """Return a MySQLServer object from a UUID or an HOST:PORT.
    """
    uuid = _retrieve_uuid_object(server_id)

    server = _server.MySQLServer.fetch(uuid)
    if not server:
        raise _errors.ServerError(
            "Server (%s) does not exist." % (uuid, )
            )

    if not server.group_id:
        raise _errors.GroupError(
            "Server (%s) does not belong to a group." % (uuid, )
            )

    if group_id is not None and group_id != server.group_id:
        raise _errors.GroupError(
            "Group (%s) does not contain server (%s)." % (group_id, uuid)
        )
    return server

def _check_server_exists(server_id):
    """Check whether a MySQLServer instance exists or not.

    :param server_id: The UUID or the host:port for the server.
    """
    server_id = _retrieve_uuid_object(server_id)

    server = _server.MySQLServer.fetch(server_id)
    if server:
        raise _errors.ServerError("Server (%s) already exists." % (server_id, ))

def _retrieve_group(group_id):
    """Return a Group object from an identifier.
    """
    group = _server.Group.fetch(group_id)
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id, ))
    return group

def _check_group_exists(group_id):
    """Check whether a group exists or not.
    """
    group = _server.Group.fetch(group_id)
    if group:
        raise _errors.GroupError("Group (%s) already exists." % (group_id, ))

def _check_shard_exists(group_id):
    """Check whether there is a shard associated with the group.
    """
    shard_id = _sharding.Shards.lookup_shard_id(group_id)
    if shard_id:
        raise _errors.GroupError(
            "Cannot erase a group (%s) which is associated to a shard (%s)." % 
            (group_id, shard_id)
        )

    shard_mapping_id = _sharding.ShardMapping.lookup_shard_mapping_id(group_id)
    if shard_mapping_id:
        raise _errors.GroupError(
            "Cannot erase a group (%s) which is used as a global group in a "
            "shard definition (%s)." % (group_id, shard_mapping_id)
        )

def _retrieve_uuid_object(server_id):
    """Transform an input string into a UUID object.
    """
    assert(isinstance(server_id, basestring))

    try:
        return _uuid.UUID(server_id)
    except ValueError:
        pass

    try:
        return _server.MySQLServer.discover_uuid(address=server_id)
    except ValueError:
        raise _errors.ServerError(
            "Error trying to access server identified by (%s)." % (server_id, )
        )

def _check_requirements(server):
    """Check if the server fulfils some requirements.
    """
    # Being able to connect to the server is the first requirment.
    server.connect()

    if not server.check_version_compat((5, 6, 8)):
        raise _errors.ServerError(
            "Server (%s) has an outdated version (%s). 5.6.8 or greater "
            "is required." % (server.uuid, server.version)
            )

    if not server.has_required_privileges():
        raise _errors.ServerError(
            "User (%s) does not have appropriate privileges (%s) on server "
            "(%s, %s)." % (server.user,
            ", ".join(_server.MySQLServer.ALL_PRIVILEGES),
            server.address, server.uuid)
        )

    if not server.gtid_enabled or not server.binlog_enabled:
        raise _errors.ServerError(
            "Server (%s) does not have the binary log or gtid enabled."
            % (server.uuid, )
            )

def _configure_as_slave(group, server):
    """Configure the server as a slave.
    """
    try:
        if group.master:
            master = _server.MySQLServer.fetch(group.master)
            master.connect()
            _utils.switch_master(server, master)
    except _errors.DatabaseError as error:
        _LOGGER.debug(
            "Error configuring slave (%s)...", server.uuid, exc_info=error
        )
        raise _errors.ServerError(
            "Error trying to configure Server (%s) as slave."
            % (server.uuid, )
        )
