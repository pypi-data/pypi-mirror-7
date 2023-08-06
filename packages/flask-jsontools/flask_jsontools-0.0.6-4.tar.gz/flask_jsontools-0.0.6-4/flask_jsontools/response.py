from flask import current_app, request, Response, json


class JsonResponse(Response):
    """ Response from a JSON API view """

    @staticmethod
    def _lazy_json(data, indent=None): # CHECKME: This hack prevents Flask from providing the correct 'Content-Length' header. is it ok?
        """ Lazy iterable: jsonify() only when iterated """
        yield json.dumps(data, indent=indent)

    def __init__(self, response, status=None, headers=None, **kwargs):
        """ Init a JSON response
        :param response: Response data
        :type response: *
        :param status: Status code
        :type status: int|None
        :param headers: Additional headers
        :type headers: dict|None
        """
        # Store response
        self._response_data = self.preprocess_response_data(response)

        # Init super
        indent = 2 if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr else None
        super(JsonResponse, self).__init__(
            self._lazy_json(self._response_data, indent=indent),
            headers=headers, status=status, mimetype='application/json',
            direct_passthrough=True, **kwargs)

    def preprocess_response_data(self, response):
        """ Preprocess the response data.

        Override this method to have custom handling of the response

        :param response: Return value from the view function
        :type response: *
        :return: Preprocessed value
        """
        return response

    def get_json(self):
        """ Get the response data object (preprocessed) """
        return self._response_data

    def __getitem__(self, item):
        """ Proxy method to get items from the underlying object """
        return self._response_data[item]


def normalize_response_value(rv):
    """ Normalize the response value into a 3-tuple (rv, status, headers)
        :type rv: tuple|*
        :returns: tuple(rv, status, headers)
        :rtype: tuple(Response|JsonResponse|*, int|None, dict|None)
    """
    status = headers = None
    if isinstance(rv, tuple):
        rv, status, headers = rv + (None,) * (3 - len(rv))
    return rv, status, headers


def make_json_response(rv):
    """ Make JsonResponse
    :param rv: Response: the object to encode, or tuple (response, status, headers)
    :type rv: tuple|*
    :rtype: JsonResponse
    """
    # Tuple of (response, status, headers)
    rv, status, headers = normalize_response_value(rv)

    # JsonResponse
    if isinstance(rv, JsonResponse):
        return rv

    # Data
    return JsonResponse(rv, status, headers)
