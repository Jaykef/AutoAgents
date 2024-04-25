#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autoagents.actions import Requirement, CreateRoles
from autoagents.roles import Role


class Manager(Role):
    def __init__(self, name="Ethan", profile="Manager", goal="Efficiently to finish the tasks or solve the problem",
                 constraints="", mock_mode=False, **kwargs):
        super().__init__(name, profile, goal, constraints, mock_mode=mock_mode, **kwargs)
        self._init_actions([CreateRoles])
        self._watch([Requirement])
