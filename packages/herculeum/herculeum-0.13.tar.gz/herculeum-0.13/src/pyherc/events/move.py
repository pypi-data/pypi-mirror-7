# -*- coding: utf-8 -*-

#   Copyright 2010-2014 Tuukka Turto
#
#   This file is part of pyherc.
#
#   pyherc is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   pyherc is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with pyherc.  If not, see <http://www.gnu.org/licenses/>.

"""
Classes for move events
"""
from pyherc.events.event import Event


class MoveEvent(Event):
    """
    Event that can be used to relay information about moving

    .. versionadded:: 0.4
    """
    def __init__(self, mover, old_location, direction, affected_tiles):
        """
        Default constructor

        :param mover: character moving around
        :type mover: Character
        :param affected_tiles: tiles affected by event
        :type affected_tiles: [(int, int)]
        """
        super().__init__(event_type='move',
                         level=mover.level,
                         location=mover.location,
                         affected_tiles=affected_tiles)

        self.mover = mover
        self.old_location = old_location
        self.direction = direction

    def get_description(self, point_of_view):
        """
        Description of the event

        :param point_of_view: point of view for description
        :type point_of_view: Character
        :returns: description of the event
        :rtype: string
        """
        if point_of_view == self.mover:
            description = 'You move'
        else:
            description = '{0} moves'.format(self.mover.name)

        return description
