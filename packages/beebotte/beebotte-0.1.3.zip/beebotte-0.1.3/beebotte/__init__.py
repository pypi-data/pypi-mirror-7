"""Python library for interfacing with Beebotte.

Contains methods for sending persistent and transient messages and for reading data.
"""

__version__ = '0.1.2'

import json
import time
import hmac
import base64
import hashlib
import requests
from email import utils
try: import urllib.parse as urllib
except ImportError: import urllib

__publicReadEndpoint__ = "/api/public/resource"
__readEndpoint__       = "/api/resource/read"
__writeEndpoint__      = "/api/resource/write"
__bulkWriteEndpoint__  = "/api/resource/bulk_write"
__eventEndpoint__      = "/api/event/write"

class BBT:
  akey     = None
  skey     = None
  hostname = None
  port     = None
  ssl      = None

  """
  Creates and maintains an object holding user credentials and connection parameters to be used as needed.

  @param akey: The user's API key (access key) to be passed along the authentication parameters.
  @param skey: The user's secret key to be used to sign API calls.
  @param hostname: The host name where the API is implemented.
  @param port: The port number.
  @param ssl: Indicates if SSL (TLS) should be used.
  """
  def __init__(self, akey, skey, hostname = "api.beebotte.com", port = "80", ssl = False):
    self.akey     = akey
    self.skey     = skey
    self.hostname = hostname
    self.port     = port
    self.ssl      = ssl

  """
  Utility function that signs the given string with the secret key using SHA1 HMAC and returns a string containing
  the access key followed by column followed by the hash in base64.

  @param stringToSign: The string data to sign.

  @return: returns a string containing the access key followed by column followed by the SHA1 HMAC of the string to sign using the secret key encoded in base64.
    This signature format is used to authenticate API calls
  """
  def sign(self, stringToSign):
    signature = hmac.new(self.skey.encode(), stringToSign.encode(), hashlib.sha1)
    return "%s:%s" % (self.akey, bytes.decode(base64.b64encode(signature.digest())))

  """
  Creates a signature of an API call to authenticate the user and verify message integrity.

  @param verb: The HTTP verb (method) in upper case.
  @param uri: the API endpoint containing the query parameters.
  @param date: The date on the caller side.
  @param c_type: The Content type header, should be application/json.
  @param c_md5: The content MD5 hash of the data to send (should be set for POST requests)

  @return: returns the signature of the API call to be added as authorization header in the request to send.
  """
  def __signRequest__(self, verb, uri, date, c_type, c_md5 = ""):
    stringToSign = "%s\n%s\n%s\n%s\n%s" % (verb, c_md5, c_type, date, uri)
    return self.sign(stringToSign)

  """
  Checks if the given response data is OK or if an error occurred

  @param response: The response containing the response status and data

  @return: The response data in JSON if the status is OK, raises an exception otherwise (with the status code and error code)
  """
  def __processResponse__(self, response):
    code    = response['status']
    data   = json.loads(response['data'])
    if code < 400:
      return data
    else:
      errcode = data['error']['code']
      errmsg  = data['error']['message']
      if code == 400:
        if errcode == 1101:
          raise AuthenticationError("Status: 400; Code 1101; Message: %s" % errmsg)
        elif errcode == 1401:
          raise ParameterError("Status: 400; Code 1401; Message: %s" % errmsg)
        elif errcode == 1403:
          raise BadRequestError("Status: 400; Code 1403; Message: %s" % errmsg)
        elif errcode == 1404:
          raise TypeError("Status: 400; Code 1404; Message: %s" % errmsg)
        elif errcode == 1405:
          raise BadTypeError("Status: 400; Code 1405; Message: %s" % errmsg)
        elif errcode == 1406:
          raise PayloadLimitError("Status: 400; Code 1406; Message: %s" % errmsg)
        else:
          raise UnexpectedError("Status: %s; Code %s; Message: %s" % (code, errcode, errmsg) )
      elif code == 405:
        if errcode == 1102:
          raise NotAllowedError("Status: 405; Code 1102; Message: %s" % errmsg)
        else:
          raise UnexpectedError("Status: %s; Code %s; Message: %s" % (code, errcode, errmsg) )
      elif code == 500:
        if errcode == 1201:
          raise InternalError("Status: 500; Code 1201; Message: %s" % errmsg)
        else:
          raise InternalError("Status: %s; Code %s; Message: %s" % (code, errcode, errmsg) )
      elif code == 404:
        if errcode == 1301:
          raise NotFoundError("Status: 404; Code 1301; Message: %s" % errmsg)
        if errcode == 1302:
          raise NotFoundError("Status: 404; Code 1302; Message: %s" % errmsg)
        if errcode == 1303:
          raise NotFoundError("Status: 404; Code 1303; Message: %s" % errmsg)
        if errcode == 1304:
          raise AlreadyExistError("Status: 404; Code 1304; Message: %s" % errmsg)
        if errcode == 1305:
          raise AlreadyExistError("Status: 404; Code 1305; Message: %s" % errmsg)
        if errcode == 1306:
          raise AlreadyExistError("Status: 404; Code 1306; Message: %s" % errmsg)
        else:
          raise UnexpectedError("Status: %s; Code %s; Message: %s" % (code, errcode, errmsg) )
      else:
        raise UnexpectedError("Status: %s; Code %s; Message: %s" % (code, errcode, errmsg) )

  """
  Sends a POST request with the given data to the given URI endpoint and returns the response data.

  @param uri: The uri endpoint.
  @param data: the data to send.
  @param auth: Indicates if the Post request should be authenticated (defaults to true).

  @return: The response data in JSON format if success, raises an error or failure.
  """
  def __postData__(self, uri, data, auth = True):
    if self.ssl:
      url = "%s://%s:%s%s" % ( 'https', self.hostname, self.port, uri )
    else:
      url = "%s://%s:%s%s" % ( 'http', self.hostname, self.port, uri )

    md5 = bytes.decode( base64.b64encode( hashlib.md5( str.encode( data ) ).digest() ) )
    date = utils.formatdate()
    if auth:
      sig = self.__signRequest__('POST', uri, date, "application/json", md5)
      headers = { 'Content-MD5': md5, 'Content-Type': 'application/json', 'Date': date, 'Authorization': sig }
    else:
      headers = { 'Content-MD5': md5, 'Content-Type': 'application/json', 'Date': date }

    r = requests.post( url, data=data, headers=headers )
    return self.__processResponse__( { 'status': r.status_code, 'data': r.text } )

  """
  Sends a GET request with the given query parameters to the given URI endpoint and returns the response data.

  @param uri: The uri endpoint.
  @param query: the query parameters in JSON format.
  @param auth: Indicates if the Post request should be authenticated (defaults to true).

  @return: The response data in JSON format if success, raises an error or failure.
  """
  def __getData__(self, uri, query, auth = True):
    if self.ssl:
      url = "%s://%s:%s%s" % ( 'https', self.hostname, self.port, uri )
    else:
      url = "%s://%s:%s%s" % ( 'http', self.hostname, self.port, uri )

    full_uri = "%s?%s" % ( uri, urllib.urlencode( query ) )
    date = utils.formatdate()
    if auth:
      sig = self.__signRequest__('GET', full_uri, date, "application/json")
      headers = { 'Content-Type': 'application/json', 'Date': date, 'Authorization': sig }
    else:
      headers = { 'Content-Type': 'application/json', 'Date': date }

    r = requests.get( url, params=query, headers=headers )
    return self.__processResponse__( { 'status': r.status_code, 'data': r.text } )

  """
  Public Read
  Reads data from the resource with the given metadata. This method expects the resource to have public access. 
  In Beebotte, resources follow a 3 level hierarchy: Device -> Service -> Resource
  Data is always associated with Resources.
  This call will not be signed (no authentication required) as the resource is public.
  
  @param owner: required the owner (username) of the resource to read from.
  @param device: required the device name.
  @param service: required the service name.
  @param resource: required the resource name to read from.
  @param limit: optional number of records to return.
  @param source: optional indicates whether to read from live data or from historical statistics. Accepts ('live', 'hour', 'day', 'week', 'month').
  @param metric: optional indicates the metric to read. This works only with $source different than 'live'. Accepts ('avg', 'min', 'max', 'count')
  
  @return: The response data in JSON format if success, raises an error or failure.
  """
  def publicRead(self, owner, device, service, resource, limit = 1, source = "live", metric = "avg" ):
    query = {'owner': owner, 'device': device, 'service': service, 'resource': resource, 'limit': limit, 'source': source, 'metric': metric}

    response = self.__getData__( __publicReadEndpoint__, query, False )
    return response;

  """
  Read
  Reads data from the resource with the given metadata. 
  In Beebotte, resources follow a 3 level hierarchy: Device -> Service -> Resource
  Data is always associated with Resources.
  This call will be signed to authenticate the calling user.
  
  @param device: required the device name.
  @param service: required the service name.
  @param resource: required the resource name to read from.
  @param limit: optional number of records to return.
  @param source: optional indicates whether to read from live data or from historical statistics. Accepts ('live', 'hour', 'day', 'week', 'month').
  @param metric: optional indicates the metric to read. This works only with $source different than 'live'. Accepts ('avg', 'min', 'max', 'count')
  
  @return: The response data in JSON format if success, raises an error or failure.
  """
  def read(self, device, service, resource, limit = 1, source = "live", metric = "avg" ):
    query = { 'device': device, 'service': service, 'resource': resource, 'limit': limit, 'source': source, 'metric': metric }

    response = self.__getData__( __readEndpoint__, query, True )
    return response;

  """
  Write (Persistent messages)
  Writes data to the resource with the given metadata. 
  In Beebotte, resources follow a 3 level hierarchy: Device -> Service -> Resource
  Data is always associated with Resources.
  This call will be signed to authenticate the calling user.
  
  @param device: required the device name.
  @param service: required the service name.
  @param resource: required the resource name to read from.
  @param value: required the value to write (persist).
  @param ts: optional timestamp in milliseconds (since epoch). If this parameter is not given, it will be automatically added with a value equal to the local system time.
  @param type: optional default to 'attribute'. This is for future use.
   
  @return: true on success, raises an error or failure.
  """
  def write(self, device, service, resource, value, ts = None, type = "attribute" ):
    body = { 'device': device, 'service': service, 'resource': resource, 'value': value, 'type': type }
    ###
    #if ts:
    #  body['ts'] = ts
    #else:
    #  body['ts'] = round(time.time() * 1000)
    ###
    response = self.__postData__( __writeEndpoint__, json.dumps(body, separators=(',', ':')), True )
    return response;

  """
  Bulk Write (Persistent messages)
  Writes an array of data in one API call. 
  In Beebotte, resources follow a 3 level hierarchy: Device -> Service -> Resource
  Data is always associated with Resources.
  This call will be signed to authenticate the calling user.
  
  @param device: required the device name.
  @param data_array: required the data array to send. Should follow the following format
    [{
      service required the service name.
      resource required the resource name to read from.
      value required the value to write (persist).
      ts optional timestamp in milliseconds (since epoch). If this parameter is not given, it will be automatically added with a value equal to the local system time.
      type optional default to 'attribute'. This is for future use.
    }]
   
  @return: true on success, raises an error or failure.
  """
  def bulkWrite(self, device, data_array ):
    body = { 'device': device, 'data': data_array }

    response = self.__postData__( __bulkWriteEndpoint__, json.dumps(body, separators=(',', ':')), True )
    return response;

  """
  Publish (Transient messages)
  Publishes data to the resource with the given metadata. The published data will not be persisted. It will only be delivered to connected subscribers. 
  In Beebotte, resources follow a 3 level hierarchy: Device -> Service -> Resource
  Data is always associated with Resources.
  This call will be signed to authenticate the calling user.
  
  @param device: required the device name.
  @param service: required the service name.
  @param resource: required the resource name to read from.
  @param data: required the data to publish (transient).
  @param ts: optional timestamp in milliseconds (since epoch). If this parameter is not given, it will be automatically added with a value equal to the local system time.
  @param source: optional additional data that will be appended to the published message. This can be a logical identifier (session id) of the originator. Use this as suits you.
   
  @return: true on success, raises an error or failure.
  """
  def publish(self, device, service, resource, data, ts = None, source = None ):
    body = { 'device': device, 'service': service, 'resource': resource, 'data': data }
    if source:
      body['source'] = source
    ###
    #if ts:
    #  body['ts'] = ts
    #else:
    #  body['ts'] = round(time.time() * 1000)
    ###

    response = self.__postData__( __eventEndpoint__, json.dumps(body, separators=(',', ':')), True )
    return response;

  """
  Client Authentication (used for the Presence and Resource subscription process)
  Signs the given subscribe metadata and returns the signature.

  @param sid: required the session id of the client.
  @param device: required the device name. Should start with 'presence:' for presence channels and starts with 'private:' for private channels.
  @param service: optional the service name.
  @param resource: optional the resource name to read from.
  @param ttl: optional the number of seconds the signature should be considered as valid (currently ignored) for future use.
  @param read: optional indicates if read access is requested.
  @param write: optional indicates if write access is requested.

  @return: JSON object containing 'auth' element with value equal to the generated signature.
  """
  def auth_client( self, sid, device, service = '*', resource = '*', ttl = 0, read = False, write = False ):
    r = 'false'
    w = 'false'
    if read:
      r = 'true'
    if write:
      w = 'true'
    stringToSign = "%s:%s.%s.%s:ttl=%s:read=%s:write=%s" % ( sid, device, service, resource, ttl, r, w )
    return self.sign(stringToSign)

"""
Utility class for dealing with Resources
Contains methods for sending persistent and transient messages and for reading data.
Mainly wrappers around Beebotte API calls. 
"""
class Resource:
  device   = None
  service  = None
  resource = None
  bbt      = None

  """
  Constructor, initializes the Resource object.
  In Beebotte, resources follow a 3level hierarchy: Device -> Service -> Resource
  Data is always associated with Resources.
  
  @param bbt: required reference to the Beebotte client connector.
  @param device: required device name.
  @param service: required service name.
  @param resource: required resource name.
  """
  def __init__(self, bbt, device, service, resource):
    self.device   = device
    self.service  = service
    self.resource = resource
    self.bbt      = bbt

  """
  Write (Persistent messages)
  Writes data to this resource. 
  This call will be signed to authenticate the calling user.
  
  @param value: required the value to write (persist).
  @param ts: optional timestamp in milliseconds (since epoch). If this parameter is not given, it will be automatically added with a value equal to the local system time.
   
  @return: true on success, raises an error or failure.
  """
  def write(self, value, ts = None):
    return self.bbt.write(self.device, self.service, self.resource, ts = ts, value = value)

  """
  Publish (Transient messages)
  Publishes data to this resource. The published data will not be persisted. It will only be delivered to connected subscribers. 
  This call will be signed to authenticate the calling user.
  
  @param data: required the data to publish (transient).
  @param ts: optional timestamp in milliseconds (since epoch). If this parameter is not given, it will be automatically added with a value equal to the local system time.
   
  @return: true on success, raises an error or failure.
  """
  def publish(self, data, ts = None):
    return self.bbt.publish(self.device, self.service, self.resource, ts = ts, data = data)

  """
  Read
  Reads data from the this resource.
  If the owner is set (value different than None) the behaviour is Public Read (no authentication).
  If the owner is None, the behaviour is authenticated read.      
  
  @param limit: optional number of records to return.
  @param owner: optional the owner (username) of the resource to read from for public read. None to read from the user's owned device.
  @param source: optional indicates whether to read from live data or from historical statistics. Accepts ('live', 'hour', 'day', 'week', 'month').
  @param metric: optional indicates the metric to read. This works only with $source different than 'live'. Accepts ('avg', 'min', 'max', 'count')
  
  @return: array of records (JSON) on success, raises an error or failure.
  """
  def read(self, limit = 1, owner = None, source = "live", metric = "avg"):
    if owner:
      return self.bbt.publicRead( owner, self.device, self.service, self.resource, limit, source, metric )
    else:
      return self.bbt.read(self.device, self.service, self.resource, limit, source, metric)

  """
  Read
  Reads the last inserted record. 
  
  @return: the last inserted record on success, raises an error or failure.
  """
  def recentVal(self):
    return self.bbt.read(self.device, self.service, self.resource)[0]

class DataPoint:
  device   = None
  service  = None
  resource = None
  value    = None
  ts       = None

  def __init__(self, value, ts, device = None, service = None, resource = None):
    self.device   = device
    self.service  = service
    self.resource = resource
    self.value    = value
    self.ts       = ts

  @classmethod
  def fromJSON(cls, params):
    #return cls( params['device'], params['service'], params['resource'], params['value'], params['ts'] )
    return cls( value = params['value'], ts = params['ts'] )

  def toJSON(self, owner = None):
    return {'owner': owner, 'device': self.device, 'service': self.service, 'resource': self.resource, 'value': self.value, 'ts': self.ts}

class AuthenticationError(Exception):
    pass

class InternalError(Exception):
    pass

class NotFoundError(Exception):
    pass

class AlreadyExistError(Exception):
    pass

class NotAllowedError(Exception):
    pass

class UsageLimitError(Exception):
    pass

class PayloadLimitError(Exception):
    pass

class UnexpectedError(Exception):
    pass

class BadRequestError(Exception):
    pass

class ParameterError(Exception):
    pass

class TypeError(Exception):
    pass

class BadTypeError(Exception):
    pass

