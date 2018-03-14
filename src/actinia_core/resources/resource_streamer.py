# -*- coding: utf-8 -*-
"""
This module is responsible to answer requests for file based resources.
"""
from flask import jsonify, make_response
from flask_restful import Resource
from flask import send_from_directory
import os
from actinia_core.resources.common.config import global_config
from actinia_core.resources.common.app import auth
from actinia_core.resources.common.logging_interface import log_api_call


__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RequestStreamerResource(Resource):
    """
    This class is responsible to answer requests
    for file based resources and to stream them.
    """
    decorators = [log_api_call, auth.login_required]

    def get(self, user_id, resource_id, file_name):
        """Get the file based resource as HTTP attachment

        Args:
            user_id (str): The unique user name/id
            resource_id (str): The id of the resource
            file_name (str): The name of the file to send as attachment

        Returns:
            flask.Response: A HTTP response with the
                            file as attachment in case of success or
                            JSON payload containing the error status
                            and a message

            The HTTP status 200 header::

                Content-Disposition: attachment; filename=my_accumulation.tiff
                Content-Length: 3469
                Content-Type: image/tiff
                Last-Modified: Tue, 07 Jun 2016 10:34:17 GMT
                Cache-Control: public, max-age=43200
                Expires: Tue, 07 Jun 2016 22:34:18 GMT
                ETag: "1465295657.53-3469-665590421"
                Date: Tue, 07 Jun 2016 10:34:18 GMT


            The HTTP status 400 response JSON contents::

                {
                  "Messages": "Resource does not exist",
                  "Status": "error"
                }

        """

        resource_dir = global_config.GRASS_RESOURCE_DIR
        user_export_path =os.path.join(resource_dir, user_id)
        resource_export_path = os.path.join(user_export_path, resource_id)
        resource_export_file_path = os.path.join(resource_export_path, file_name)

        if os.path.exists(resource_export_file_path) is True and \
                          os.access(resource_export_file_path, os.R_OK) is True:

            return send_from_directory(resource_export_path,
                                       file_name, as_attachment=True)
        else:
            return make_response(jsonify({"status":"error",
                                          "message":"Resource does not exist"}), 400)
