import logging

from suds.client import Client
from suds import WebFault

from .exceptions import ConnectError
from .types import (
    RecordData, RecipientResult, MergeResult, DeleteResult, LoginResult, ServerAuthResult)

log = logging.getLogger(__name__)


class InteractClient(object):

    """ Interact Client Class

    Provides access to the methods defined by the Responsys Interact API. Example setup:

        >>> client = InteractClient(username, password, pod)
        >>> client.connect()
        >>> client.merge_list_members(interact_object, records, merge_rules)
        >>> client.disconnect()

    Using the client class as a context manager will automatically connect using the credentials
    provided, and disconnect upon context exit:

        >>> with InteractClient(username, password, pod) as client:
        ...     client.merge_list_members(interact_object, records, merge_rules)

    Since responsys limits the number of active sessions per account, this can help ensure you
    don't leave unused connections open.
    """

    WSDLS = {
        '2': 'https://ws2.responsys.net/webservices/wsdl/ResponsysWS_Level1.wsdl',
        '5': 'https://ws5.responsys.net/webservices/wsdl/ResponsysWS_Level1.wsdl',
        'rtm4': 'https://rtm4.responsys.net/tmws/services/TriggeredMessageWS?wsdl',
        'rtm4b': 'https://rtm4b.responsys.net/tmws/services/TriggeredMessageWS?wsdl',
    }

    ENDPOINTS = {
        '2': 'https://ws2.responsys.net/webservices/services/ResponsysWSService',
        '5': 'https://ws5.responsys.net/webservices/services/ResponsysWSService',
        'rtm4': 'http://rtm4.responsys.net:80/tmws/services/TriggeredMessageWS',
        'rtm4b': 'http://rtm4b.responsys.net:80/tmws/services/TriggeredMessageWS',
    }

    @property
    def wsdl(self):
        return self.WSDLS[self.pod]

    @property
    def endpoint(self):
        return self.ENDPOINTS[self.pod]

    def __init__(self, username, password, pod, client=None):
        self.username = username
        self.password = password
        self.pod = pod
        self.client = client or Client(self.wsdl, location=self.endpoint)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type_, value, traceback):
        self.disconnect()

    def connect(self):
        """ Connects to the Responsys soap service

        Uses the credentials passed to the client init to login and setup the session id returned.
        Returns True on successful connection, otherwise False.
        """
        try:
            login_result = self.login(self.username, self.password)
        except WebFault as e:
            account_fault = getattr(e.fault.detail, 'AccountFault', None)
            if account_fault:
                log.error('Login failed, invalid username or password')
            else:
                log.error('Login failed, unknown error', exc_info=True)
            raise ConnectError("Failed to connect to soap service")

        self.__set_session(login_result.session_id)
        return True

    def disconnect(self):
        """ Disconnects from the Responsys soap service

        Calls the service logout method and destroys the client's session information. Returns
        True on success, False otherwise.
        """
        if self.logout():
            self.__unset_session()
            return True
        return False

    # Session Management Methods
    def login(self, username, password):
        """ Responsys.login soap call

        Accepts username and password for authentication, returns a LoginResult object.
        """
        return LoginResult(self.client.service.login(username, password))

    def logout(self):
        """ Responsys.logout soap call

        Returns True on success, False otherwise.
        """
        return self.client.service.logout()

    def login_with_certificate(self, encrypted_server_challenge):
        """ Responsys.loginWithCertificate soap call

        Accepts encrypted_server_challenge for login. Returns LoginResult.
        """
        return LoginResult(self.client.service.loginWithCertificate(encrypted_server_challenge))

    def authenticate_server(self, username, client_challenge):
        """ Responsys.authenticateServer soap call

        Accepts username and client_challenge to authenciate. Returns ServerAuthResult.
        """
        return ServerAuthResult(self.client.service.authenticateServer(username, client_challenge))

    def __set_session(self, session_id):
        """ Set appropriate session header on suds client """
        session_header = self.client.factory.create('SessionHeader')
        session_header.sessionId = session_id
        self.client.set_options(soapheaders=session_header)

    def __unset_session(self):
        """ Remove session header from current suds client """
        self.client.set_options(soapheaders=())

    # List Management Methods
    def merge_list_members(self, list_, record_data, merge_rule):
        """ Responsys.mergeListMembers call

        Accepts:
            InteractObject list_
            RecordData record_data
            ListMergeRule merge_rule

        Returns a MergeResult
        """
        list_ = list_.get_soap_object(self.client)
        record_data = record_data.get_soap_object(self.client)
        merge_rule = merge_rule.get_soap_object(self.client)
        return MergeResult(self.client.service.mergeListMembers(list_, record_data, merge_rule))

    def merge_list_members_RIID(self, list_, record_data, merge_rule):
        """ Responsys.mergeListMembersRIID call

        Accepts:
            InteractObject list_
            RecordData record_data
            ListMergeRule merge_rule

        Returns a RecipientResult
        """
        list_ = list_.get_soap_object(self.client)
        result = self.client.service.mergeListMembersRIID(list_, record_data, merge_rule)
        return RecipientResult(result.recipientResult)

    def delete_list_members(self, list_, query_column, ids_to_delete):
        """ Responsys.deleteListMembers call

        Accepts:
            InteractObject list_
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list ids_to_delete

        Returns a list of DeleteResult instances
        """
        list_ = list_.get_soap_object(self.client)
        result = self.client.service.deleteListMembers(list_, query_column, ids_to_delete)
        if hasattr(result, '__iter__'):
            return [DeleteResult(result) for delete_result in result]
        return [DeleteResult(result)]

    def retrieve_list_members(self, list_, query_column, field_list, ids_to_retrieve):
        """ Responsys.retrieveListMembers call

        Accepts:
            InteractObject list_
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list field_list
            list ids_to_retrieve

        Returns a RecordData instance
        """
        list_ = list_.get_soap_object(self.client)
        result = self.client.service.retrieveListMembers(
            list_, query_column, field_list, ids_to_retrieve)
        return RecordData(result.recordData)

    # Table Management Methods
    def delete_table_records(self, table, query_column, ids_to_delete):
        """ Responsys.deleteTableRecords call

        Accepts:
            InteractObject table
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list ids_to_delete

        Returns a list of DeleteResult instances
        """
        table = table.get_soap_object()
        result = self.client.service.deleteTableRecords(table, query_column, ids_to_delete)
        if hasattr(result, '__iter__'):
            return [DeleteResult(result) for delete_result in result]
        return [DeleteResult(result)]

    def merge_table_records_with_pk(self, table, record_data, insert_on_no_match, update_on_match):
        """ Responsys.mergeTableRecordsWithPK call

        Accepts:
            InteractObject table
            RecordData record_data
            string insert_on_no_match
            string update_on_match

        Returns a RecipientResult
        """
        table = table.get_soap_object()
        record_data = record_data.get_soap_object()
        return RecipientResult(self.client.service.mergeTableRecordsWithPK(
            table, record_data, insert_on_no_match, update_on_match))

    def merge_into_profile_extension(self, profile_extension, record_data, match_column,
                                     insert_on_no_match, update_on_match):
        """ Responsys.mergeIntoProfileExtension call

        Accepts:
            InteractObject profile_extension
            RecordData record_data
            string match_column
            string insert_on_no_match
            string update_on_match

        Returns a RecipientResult
        """
        profile_extension = profile_extension.get_soap_object()
        record_data = record_data.get_soap_object()
        return RecipientResult(self.client.service.mergeIntoProfileExtension(
            profile_extension, record_data, match_column, insert_on_no_match, update_on_match))

    def retrieve_table_recods(self, table, query_column, field_list, ids_to_retrieve):
        """ Responsys.mergeIntoProfileExtension call

        Accepts:
            InteractObject table
            string query_column
                possible values: 'RIID'|'EMAIL_ADDRESS'|'CUSTOMER_ID'|'MOBILE_NUMBER'
            list field_list
            list ids_to_retrieve

        Returns a RecordData
        """
        table = table.get_soap_object()
        return RecordData(self.client.service.retrieveTableRecords(
            table, query_column, field_list, ids_to_retrieve))

    # TODO: Implement
    #
    # Content Management Methods
    # Folder Management Methods,
    # Campagin Management Methods
