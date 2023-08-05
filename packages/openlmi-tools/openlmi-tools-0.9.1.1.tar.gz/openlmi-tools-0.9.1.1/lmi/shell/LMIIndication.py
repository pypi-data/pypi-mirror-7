# Copyright (C) 2012-2014 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

class LMIIndication(object):
    """
    Class representing a received indication.

    :param tuple export_methods: tuple tree for export methods

    **NOTE:** see :py:mod:`pywbem`
    """
    def __init__(self, export_methods):
        self._export_methods = export_methods

    def export_method_names(self):
        """
        :returns: tuple tree for export methods

        **NOTE:** see :py:mod:`pywbem`
        """
        return self._export_methods.keys()

    def exported_objects(self):
        """
        :returns: list of exported :py:class:`CIMInstance` objects
        """
        result = []
        for m in self._export_methods.values():
            for obj in m.values():
                result.append(obj)
        return result
