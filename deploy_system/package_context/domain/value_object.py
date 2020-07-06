# coding=utf-8
"""Value object VersionNumber for use in Package entity."""

# Import built-in modules
import re


class VersionNumber(str):
    def __init__(self, version_string):
        if self.validate(version_string):
            self.version_string = version_string

    def __str__(self):
        return self.version_string

    @staticmethod
    def validate(version_string):
        """Validate if a string matches the format of version number.

        Valid version number string examples:
        - 2017
        - 2016-ext
        - 1.2.35
        - 2.5-beta
        - 3.0.11.2
        - 2.4.5a

        regex: https://regex101.com/r/nsE0mu/1

        Args:
            version_string (str): The version number string to be validated.

        Returns (bool): Whether the version number string is valid.

        """

        regex = r'^\d+(\.\d+)*(-?[a-z]+)?$'

        match = re.match(regex, version_string)
        if match:
            return True
        raise ValueError('Version number string not match valid format.')

    @staticmethod
    def validate_internal(version_string):
        """Validate if a string matches the format of version number.

        Valid version number string examples:
        - 1.2.35
        - 0.0.0
        - 0.35.112

        regex: https://regex101.com/r/nsE0mu/2

        Args:
            version_string (str): The version number string to be validated.

        Returns (bool): Whether the version number string is valid.

        """

        regex = r'^\d+(\.\d+){2}$'

        match = re.match(regex, version_string)
        if match:
            return True
        raise ValueError('Version number string not match valid format.')
