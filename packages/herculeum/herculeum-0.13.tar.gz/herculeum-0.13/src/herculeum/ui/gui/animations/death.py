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
Classes for death animations
"""
from .animation import Animation


class DeathAnimation(Animation):
    """
    Generic dying animation

    .. versionadded:: 0.12
    """
    def __init__(self, event):
        """
        Default constructor
        """
        super().__init__(event)

        self.deceased = event.deceased

    def trigger(self, ui):
        """
        Trigger this animation
        """
        glyphs = [x for x in ui.view.items()
                  if (hasattr(x, 'entity'))
                  and (x.entity == self.deceased)]

        for glyph in glyphs:
            ui.view.scene().removeItem(glyph)

        if self.deceased == ui.model.player:
            ui.EndScreenRequested.emit()
