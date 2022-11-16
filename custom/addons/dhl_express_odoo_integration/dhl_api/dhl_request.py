import re
import requests
import logging
import time
from odoo import _
from requests import Request, Session
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from odoo.exceptions import ValidationError
from odoo.addons.dhl_express_odoo_integration.dhl_api.utils import dict2xml, smart_encode
from odoo.addons.dhl_express_odoo_integration.dhl_api.dhl_response import Response
from odoo.addons.dhl_express_odoo_integration.dhl_api.exception import ConnectionError
_logger = logging.getLogger(__name__)

DHL_API_XSD = {
        'DCTRequest' : 'DCT-req.xsd',
        }

class DHL_API():

    def __init__(self, prod_environment, method="POST", **kwargs):
        """DHL API class constructor."""
        if not prod_environment :
            self.url = 'https://xmlpitest-ea.dhl.com/XMLShippingServlet'
        else:
            self.url = 'https://xmlpi-ea.dhl.com/XMLShippingServlet'
        self.response = None
        self.request = None
        self.verb = None
        self.method = method
        self.site_id = kwargs.get('site_id', '')
        self.password = kwargs.get('password', '')
        self.timeout = kwargs.get('timeout') or 500
        self.proxies = dict()
        self.session = Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def build_request_headers(self):
        headers = {
            "Content-Type": "application/xml",
        }
        return headers

    def build_request_data(self, verb, data, version):
        xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        if not version :
            xml += "<req:{verb} xmlns:req=\"http://www.dhl.com\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">".format(verb=self.verb)
        else :
            xml += "<req:{verb} xmlns:req=\"http://www.dhl.com\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" schemaVersion=\"{schema}\">".format(verb=self.verb, schema=version)
        if data :
            if isinstance(data, str) :
                if data.startswith('<%s>' % verb) :
                    data = data.replace("<%s>" % verb, '')
                    data = data.replace("</%s>" % verb, '')
            xml += data
        xml += "</req:{verb}>".format(verb=self.verb)
        return xml

    def build_request(self, verb, data, version):
        self.verb = verb
        self._request_dict = data
        headers = self.build_request_headers()
        requestData = self.build_request_data(verb, data, version)
        request = Request(self.method, self.url, data=requestData, headers=headers)
        self.request = request.prepare()

    def _reset(self):
        self.verb = None
        self._request_dict = None
        self._response_content = None
        self._time = time.time()
        self._response_error = None
        self._resp_body_errors = []

    def execute_request(self):
        _logger.debug("REQUEST : %s %s" % (self.request.method, self.request.url))
        _logger.debug('headers=%s' % self.request.headers)
        _logger.debug('body=%s' % self.request.body)
        self.response = self.session.send(self.request, verify=True, proxies=self.proxies, timeout=self.timeout, allow_redirects=True)
        _logger.debug('RESPONSE')
        _logger.debug('Elapsed time=%s' % self.response.elapsed)
        _logger.debug('Status code=%s' % self.response.status_code)
        _logger.debug('Headers=%s' % self.response.headers)
        _logger.debug('Content=%s' % self.response.text)

    def process_response(self, parse_response=True):
        """Post processing of the response"""
        self.response = Response(self.response, verb=self.verb, parse_response=parse_response)
        # set for backward compatibility
        self._response_content = self.response.content
        if self.response.status_code != 200:
            self._response_error = self.response.reason

    def _get_resp_body_errors(self):
        """Parses the response content to pull errors.

        Child classes should override this method based on what the errors in the
        XML response body look like. They can choose to look at the 'OperationSuccess',
        'ErrorMessage' or whatever other fields the service returns.
        the implementation below is the original code that was part of error()
        """
        if self._resp_body_errors and len(self._resp_body_errors) > 0:
            return self._resp_body_errors
        errors = []
        if self.verb is None:
            return errors
        dom = self.response.dom()
        if dom is None:
            return errors
        if dom.tag == 'ErrorResponse' or dom.tag == 'ShipmentValidateErrorResponse' :
            condition = dom.findall('Response/Status/Condition')
            error_msg = "Error Code : %s - %s" % (condition[0][0].text, condition[0][1].text)
            try:
                eMsg = smart_encode(error_msg)
                errors.append(eMsg)
            except IndexError:
                pass

        if dom.tag:
            condition = dom.findall('GetQuoteResponse/Note/Condition')
            if condition:
                error_msg = "Error Code : %s - %s" % (condition[0][0].text, condition[0][1].text)
                try:
                    eMsg = smart_encode(error_msg)
                    errors.append(eMsg)
                except IndexError:
                    pass
                if errors:
                    _logger.error("{verb}: {message}\n\n".format(verb=self.verb, message="\n".join(errors)))
                    return errors

        self._resp_body_errors = errors
        if hasattr(self.response.reply, "ErrorResponse") :
            response_data_object = getattr(self.response.reply, "ErrorResponse")
            if response_data_object.Response.Status.ActionStatus == 'Error' :
                _logger.error("{verb}: {message}\n\n".format(verb=self.verb, message="\n".join(errors)))
                return errors
        if hasattr(self.response.reply, "ShipmentValidateErrorResponse") :
            response_data_object = getattr(self.response.reply, "ShipmentValidateErrorResponse")
            _logger.error("{verb}: {message}\n\n".format(verb=self.verb, message="\n".join(errors)))
            return errors
        return []

    def error(self):
        "Builds and returns the api error message."
        error_array = []
        if self._response_error :
            error_array.append(self._response_error)
        error_array.extend(self._get_resp_body_errors())
        if len(error_array) > 0:
            # Force all errors to be unicode in a proper way
            error_array = [smart_encode(e) for e in error_array]
            error_string = "{verb}: {message}".format(verb=self.verb, message=", ".join(error_array))
            return error_string
        return None

    def error_check(self):
        """Checked the Error in response body"""
        estr = self.error()
        if estr :
            _logger.error(estr)
            raise ConnectionError(estr, self.response)

    def execute(self, verb, data=None, version=False):
        "Executes the HTTP request."
        _logger.debug("Execute : verb=%s data=%s" % (verb, data))
        self._reset()
        self.build_request(verb, data, version)
#         self.generate_cdiscount_token()
        self.execute_request()
        if hasattr(self.response, 'content'):
            self.process_response()
            self.error_check()
#             self.api_call_log(str(self.response.dict()), 'response')
        _logger.debug("Total Time=%s" % (time.time() - self._time))
        return self.response
