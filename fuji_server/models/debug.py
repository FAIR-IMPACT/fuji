# SPDX-FileCopyrightText: 2020 PANGAEA (https://www.pangaea.de/)
#
# SPDX-License-Identifier: MIT

from fuji_server import util
from fuji_server.models.base_model_ import Model


class Debug(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self):
        """Debug - a model defined in Swagger"""
        self.swagger_types = {}

        self.attribute_map = {}

    @classmethod
    def from_dict(cls, dikt) -> "Debug":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Debug of this Debug.  # noqa: E501
        :rtype: Debug
        """
        return util.deserialize_model(dikt, cls)
