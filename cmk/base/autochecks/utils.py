#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from __future__ import annotations

import ast
from typing import Any, Mapping, NamedTuple, Sequence

from cmk.utils.type_defs import CheckPluginName, Item

from cmk.base.check_utils import LegacyCheckParameters


# If we switched to something less stupid than "LegacyCheckParameters", see
# if we can use pydantic
class AutocheckEntry(NamedTuple):
    check_plugin_name: CheckPluginName
    item: Item
    parameters: LegacyCheckParameters
    service_labels: Mapping[str, str]

    @staticmethod
    def _parse_parameters(parameters: object) -> LegacyCheckParameters:
        # Make sure it's a 'LegacyCheckParameters' (mainly done for mypy).
        if parameters is None or isinstance(parameters, (dict, tuple, list, str)):
            return parameters
        # I have no idea what else it could be (LegacyCheckParameters is quite pointless).
        raise ValueError(f"Invalid autocheck: invalid parameters: {parameters!r}")

    @classmethod
    def load(cls, raw_dict: Mapping[str, Any]) -> AutocheckEntry:
        return cls(
            check_plugin_name=CheckPluginName(raw_dict["check_plugin_name"]),
            item=None if (raw_item := raw_dict["item"]) is None else str(raw_item),
            parameters=cls._parse_parameters(raw_dict["parameters"]),
            service_labels={str(n): str(v) for n, v in raw_dict["service_labels"].items()},
        )

    def dump(self) -> Mapping[str, Any]:
        return {
            "check_plugin_name": str(self.check_plugin_name),
            "item": self.item,
            "parameters": self.parameters,
            "service_labels": self.service_labels,
        }


class AutochecksSerializer:
    @staticmethod
    def serialize(entries: Sequence[AutocheckEntry]) -> bytes:
        return ("[\n%s]\n" % "".join(f"  {e.dump()!r},\n" for e in entries)).encode("utf-8")

    @staticmethod
    def deserialize(raw: bytes) -> Sequence[AutocheckEntry]:
        return [AutocheckEntry.load(d) for d in ast.literal_eval(raw.decode("utf-8"))]
