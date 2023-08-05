# Copyright 2013 Cloudera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implements all necessary Impala HiveServer 2 RPC functionality."""

# This work builds off of:
# 1. the Hue interface:
#       hue/apps/beeswax/src/beeswax/server/dbms.py
#       hue/apps/beeswax/src/beeswax/server/hive_server2_lib.py
#       hue/desktop/core/src/desktop/lib/thrift_util.py
# 2. the Impala shell:
#       Impala/shell/impala_shell.py

import datetime
import socket
import operator
import exceptions
import re

from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TBufferedTransport, TTransportException
from thrift.protocol.TBinaryProtocol import TBinaryProtocol

from impala.error import RPCError, err_if_rpc_not_ok
from impala.cli_service import TCLIService
from impala.cli_service.ttypes import (TOpenSessionReq, TFetchResultsReq,
        TCloseSessionReq, TExecuteStatementReq, TGetInfoReq, TGetInfoType,
        TTypeId, TFetchOrientation, TGetResultSetMetadataReq, TStatusCode,
        TGetColumnsReq, TGetSchemasReq, TGetTablesReq, TGetFunctionsReq,
        TGetOperationStatusReq, TOperationState, TCancelOperationReq,
        TCloseOperationReq, TGetLogReq)

# mapping between Thrift TTypeId (in schema) and TColumnValue (in returned rows)
# helper object for converting from TRow to something friendlier
_TTypeId_to_TColumnValue_getters = {
        'BOOLEAN_TYPE': operator.attrgetter('boolVal'),
        'TINYINT_TYPE': operator.attrgetter('byteVal'),
        'SMALLINT_TYPE': operator.attrgetter('i16Val'),
        'INT_TYPE': operator.attrgetter('i32Val'),
        'BIGINT_TYPE': operator.attrgetter('i64Val'),
        'TIMESTAMP_TYPE': operator.attrgetter('stringVal'),
        'FLOAT_TYPE': operator.attrgetter('doubleVal'),
        'DOUBLE_TYPE': operator.attrgetter('doubleVal'),
        'STRING_TYPE': operator.attrgetter('stringVal')
}

# the type specifiers returned from GetColumns use the strings from
# com.cloudera.impala.catalog.PrimitiveType; here we map those strings to
# TTypeId strings specified in TCLIService
_PrimitiveType_to_TTypeId = {
        'BOOLEAN': 'BOOLEAN_TYPE',
        'TINYINT': 'TINYINT_TYPE',
        'SMALLINT': 'SMALLINT_TYPE',
        'INT': 'INT_TYPE',
        'BIGINT': 'BIGINT_TYPE',
        'TIMESTAMP': 'TIMESTAMP_TYPE',
        'FLOAT': 'FLOAT_TYPE',
        'DOUBLE': 'DOUBLE_TYPE',
        'STRING': 'STRING_TYPE',
}

# datetime only supports 6 digits of microseconds but Impala supports 9.
# If present, the trailing 3 digits will be ignored without warning.
_TIMESTAMP_PATTERN = re.compile(r'(\d+-\d+-\d+ \d+:\d+:\d+(\.\d{,6})?)')

def _parse_timestamp(value):
    if value:
        match = _TIMESTAMP_PATTERN.match(value)
        if match:
            if match.group(2):
                format = '%Y-%m-%d %H:%M:%S.%f'
                # use the pattern to truncate the value
                value = match.group()
            else:
                format = '%Y-%m-%d %H:%M:%S'
            value = datetime.datetime.strptime(value, format)
        else:
            raise Exception(
                    'Cannot convert "{}" into a datetime'.format(value))
    else:
        value = None
    return value


# TODO: Add another decorator that runs the function in its own thread
def threaded(func):
    raise NotImplementedError

def retry(func):
    # Retries RPCs after closing/reopening transport
    # `service` must be the first arg in args or must be a kwarg

    def wrapper(*args, **kwargs):
        # get the thrift transport
        if 'service' in kwargs:
            transport = kwargs['service']._iprot.trans
        elif len(args) > 0 and isinstance(args[0], TCLIService.Client):
            transport = args[0]._iprot.trans
        else:
            raise RPCError("RPC function does not have expected 'service' arg")

        tries_left = 3
        while tries_left > 0:
            try:
                if not transport.isOpen():
                    transport.open()
                return func(*args, **kwargs)
            except socket.error as e:
                pass
            except TTransportException as e:
                pass
            except Exception as e:
                raise
            transport.close()
            tries_left -= 1
        raise

    return wrapper

# _get_socket and _get_transport based on the Impala shell impl
def _get_socket(host, port, use_ssl, ca_cert):
    if use_ssl:
        from thrift.transport.TSSLSocket import TSSLSocket
        if ca_cert is None:
            return TSSLSocket(host, port, validate=False)
        else:
            return TSSLSocket(host, port, validate=True, ca_certs=ca_cert)
    else:
        return TSocket(host, port)

def _get_transport(sock, host, use_ldap, ldap_user, ldap_password, use_kerberos,
        kerberos_service_name):
    if not use_ldap and not use_kerberos:
        return TBufferedTransport(sock)
    try:
      import saslwrapper as sasl
    except ImportError:
      import sasl
    from impala.thrift_sasl import TSaslClientTransport
    def sasl_factory():
        sasl_client = sasl.Client()
        sasl_client.setAttr("host", host)
        if use_ldap:
            sasl_client.setAttr("username", ldap_user)
            sasl_client.setAttr("password", ldap_password)
        else:
            sasl_client.setAttr("service", kerberos_service_name)
        sasl_client.init()
        return sasl_client
    if use_kerberos:
        return TSaslClientTransport(sasl_factory, "GSSAPI", sock)
    else:
        return TSaslClientTransport(sasl_factory, "PLAIN", sock)

def connect_to_impala(host, port, timeout=45, use_ssl=False, ca_cert=None,
        use_ldap=False, ldap_user=None, ldap_password=None, use_kerberos=False,
        kerberos_service_name='impala'):
    sock = _get_socket(host, port, use_ssl, ca_cert)
    sock.setTimeout(timeout * 1000.)
    transport = _get_transport(sock, host, use_ldap, ldap_user, ldap_password,
                               use_kerberos, kerberos_service_name)
    transport.open()
    protocol = TBinaryProtocol(transport)
    service = TCLIService.Client(protocol)
    return service

def close_service(service):
    service._iprot.trans.close()

def reconnect(service):
    service._iprot.trans.close()
    service._iprot.trans.open()

@retry
def open_session(service, user, configuration=None):
    req = TOpenSessionReq(username=user, configuration=configuration)
    resp = service.OpenSession(req)
    err_if_rpc_not_ok(resp)
    return resp.sessionHandle

@retry
def close_session(service, session_handle):
    req = TCloseSessionReq(sessionHandle=session_handle)
    resp = service.CloseSession(req)
    err_if_rpc_not_ok(resp)

@retry
def execute_statement(service, session_handle, statement, configuration=None):
    req = TExecuteStatementReq(sessionHandle=session_handle,
                               statement=statement, confOverlay=configuration)
    resp = service.ExecuteStatement(req)
    err_if_rpc_not_ok(resp)
    return resp.operationHandle

@retry
def get_result_schema(service, operation_handle):
    if not operation_handle.hasResultSet:
        return None
    req = TGetResultSetMetadataReq(operationHandle=operation_handle)
    resp = service.GetResultSetMetadata(req)
    err_if_rpc_not_ok(resp)

    schema = []
    for column in resp.schema.columns:
        name = column.columnName
        type_ = TTypeId._VALUES_TO_NAMES[
                column.typeDesc.types[0].primitiveEntry.type]
        schema.append((name, type_))

    return schema

@retry
def fetch_results(service, operation_handle, schema=None, max_rows=100,
                  orientation=TFetchOrientation.FETCH_NEXT):
    if not operation_handle.hasResultSet:
        return None

    # the schema is necessary to pull the proper values (i.e., coalesce)
    if schema is None:
        schema = get_result_schema(service, operation_handle)

    req = TFetchResultsReq(operationHandle=operation_handle,
                           orientation=orientation,
                           maxRows=max_rows)
    resp = service.FetchResults(req)
    err_if_rpc_not_ok(resp)

    rows = []
    for trow in resp.results.rows:
        row = []
        for (i, col_val) in enumerate(trow.colVals):
            type_ = schema[i][1]
            value = _TTypeId_to_TColumnValue_getters[type_](col_val).value
            if type_ == 'TIMESTAMP_TYPE':
                value = _parse_timestamp(value)
            row.append(value)
        rows.append(tuple(row))

    return rows

@retry
def get_current_database(service, session_handle):
    raise NotImplementedError

@retry
def get_databases(service, session_handle):
    req = TGetSchemasReq(sessionHandle=session_handle, schemaName='.*')
    resp = service.GetSchemas(req)
    err_if_rpc_not_ok(resp)
    return resp.operationHandle

@retry
def database_exists(service, session_handle, db_name):
    req = TGetSchemasReq(sessionHandle=session_handle, schemaName=db_name)
    resp = service.GetSchemas(req)
    err_if_rpc_not_ok(resp)
    operation_handle = resp.operationHandle
    # this only fetches default max_rows, but there should only be one row ideally
    results = fetch_results(service=service, operation_handle=operation_handle)
    exists = False
    for result in results:
        if result[0] == db_name:
            exists = True
    close_operation(service, operation_handle)
    return exists

@retry
def get_tables(service, session_handle, database_name='.*'):
    req = TGetTablesReq(sessionHandle=session_handle,
                        schemaName=database_name,
                        tableName='.*')
    resp = service.GetTables(req)
    err_if_rpc_not_ok(resp)
    return resp.operationHandle

@retry
def table_exists(service, session_handle, table_name, database_name='.*'):
    req = TGetTablesReq(sessionHandle=session_handle,
                        schemaName=database_name,
                        tableName=table_name)
    resp = service.GetTables(req)
    err_if_rpc_not_ok(resp)
    operation_handle = resp.operationHandle
    # this only fetches default max_rows, but there should only be one row ideally
    results = fetch_results(service=service, operation_handle=operation_handle)
    exists = False
    for result in results:
        if result[2] == table_name:
            exists = True
    close_operation(service, operation_handle)
    return exists

@retry
def get_table_schema(service, session_handle, table_name, database_name='.*'):
    req = TGetColumnsReq(sessionHandle=session_handle,
                         schemaName=database_name,
                         tableName=table_name,
                         columnName='.*')
    resp = service.GetColumns(req)
    err_if_rpc_not_ok(resp)
    return resp.operationHandle

@retry
def get_functions(service, session_handle, database_name='.*'):
    # TODO: need to test this one especially
    req = TGetFunctionsReq(sessionHandle=session_handle,
                           schemaName=database_name,
                           functionName='.*')
    resp = service.GetFunctions(req)
    err_if_rpc_not_ok(resp)
    return resp.operationHandle

@retry
def get_operation_status(service, operation_handle):
    req = TGetOperationStatusReq(operationHandle=operation_handle)
    resp = service.GetOperationStatus(req)
    err_if_rpc_not_ok(resp)
    return TOperationState._VALUES_TO_NAMES[resp.operationState]

@retry
def cancel_operation(service, operation_handle):
    req = TCancelOperationReq(operationHandle=operation_handle)
    resp = service.CancelOperation(req)
    err_if_rpc_not_ok(resp)

@retry
def close_operation(service, operation_handle):
    req = TCloseOperationReq(operationHandle=operation_handle)
    resp = service.CloseOperation(req)
    err_if_rpc_not_ok(resp)

@retry
def get_log(service, operation_handle):
    req = TGetLogReq(operationHandle=operation_handle)
    resp = service.GetLog(req)
    err_if_rpc_not_ok(resp)
    return resp.log

def ping(service, session_handle):
    req = TGetInfoReq(sessionHandle=session_handle,
                      infoType=TGetInfoType.CLI_SERVER_NAME)
    try:
        resp = service.GetInfo(req)
    except TTransportException as e:
        return False

    try:
        err_if_rpc_not_ok(resp)
    except RPCError as e:
        return False
    return True
