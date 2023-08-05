"""
***************
configs.section
***************

This module contains the :class:`Section <Section>` class.
"""

class Section:
    """INI configuration section.

    A Section instance stores both key-value and flag items, in ``dict_props`` and ``list_props`` attributes respectively.

    It is possible to iterate over a section; flag values are listed first, then key-value items.
    """

    def __init__(self):
        self.dict_props = {}
        self.list_props = []

    def get_values(self):
        """Gets section values.

        If section contains only flag values, a list is returned.

        If section contains only key-value items, a dictionary is returned.

        If section contains both flag and key-value items, a tuple of both is returned.
        """

        if self.list_props and self.dict_props:
            return self.list_props, self.dict_props

        return self.list_props or self.dict_props or None

    def get(self, key: str):
        """Tries to get a value from the dict_props by the given key.

        :param key: lookup key.
        :returns: value if key exists (str, bool, int, or float), None otherwise.
        """

        return self.dict_props.get(key)

    def _get_value_type(self, value):
        """Checks if the given value is boolean, float, int, of str.

        Returns converted value if conversion is possible (str, bool, int, or float).

        :param value: value to check.
        """

        if value == 'True':
            return True
        elif value == 'False':
            return False
        else:
            try:
                return_value = int(value)
            except ValueError:
                try:
                    return_value = float(value)
                except ValueError:
                    return value

            return return_value

    def _add_dict_prop(self, key: str, value: str):
        """Adds a key-value item to section."""

        self.dict_props[key] = self._get_value_type(value)

    def _add_list_prop(self, value: str):
        """Adds a flag value to  section."""

        self.list_props.append(self._get_value_type(value))

    def __repr__(self):
        return str(self.get_values())

    def __str__(self):
        return str(self.get_values())

    def __iter__(self):
        for list_prop in self.list_props:
            yield list_prop

        for dict_prop in self.dict_props:
            yield dict_prop

    def __getitem__(self, key):
        try:
            return self.dict_props[key]
        except KeyError:
            pass

        try:
            return self.list_props[key]
        except (KeyError, TypeError):
            pass

        raise KeyError(key)

    def __setitem__(self, key, value):
        try:
            self.dict_props[key] = value
            return None
        except KeyError:
            pass

        try:
            self.list_props[key] = value
            return None
        except (KeyError, TypeError) as e:
            raise e

    def __eq__(self, other):
        return self.dict_props == other.dict_props and self.list_props == other.list_props
