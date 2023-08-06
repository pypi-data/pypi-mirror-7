# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.


class Mock(object):
    def __init__(self, name, handler):
        self.__name = name
        self.__handler = handler

    @property
    def expect(self):
        return self.__handler.expect(self.__name)

    @property
    def object(self):
        return self.__handler.object(self.__name)

    def record(self, realObject):
        # @todo In record mode, catch exceptions. Funny: there is not always a "return" key in getRecordedCalls
        return self.__handler.record(self.__name, realObject)
