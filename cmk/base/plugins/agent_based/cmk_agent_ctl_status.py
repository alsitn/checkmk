#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json

from .agent_based_api.v1 import register
from .agent_based_api.v1.type_defs import StringTable
from .utils.checkmk import ControllerSection


def parse_cmk_agent_ctl_status(string_table: StringTable) -> ControllerSection:
    r"""
    >>> parse_cmk_agent_ctl_status([['{"version":"0.1.0","ip_allowlist":[],"allow_legacy_pull":false,"connections":[{"coordinates":"localhost:8000/heute","uuid":"8ab7ba3c-b4b2-4e2f-916f-2d485474133d","local":{"connection_type":"pull-agent","cert_info":{"issuer":"Site \'heute\' local CA","from":"Wed, 02 Mar 2022 18:55:52 +0000","to":"Mon, 03 Jul 3020 18:55:52 +0000"}},"remote":"connection_refused"}]}']])
    ControllerSection(allow_legacy_pull=False, ip_allowlist=())
    """
    raw = json.loads(string_table[0][0])
    return ControllerSection(
        # Currently this is all we need. Extend on demand...
        allow_legacy_pull=bool(raw["allow_legacy_pull"]),
        ip_allowlist=tuple(str(i) for i in raw["ip_allowlist"]),
    )


register.agent_section(
    name="cmk_agent_ctl_status",
    parse_function=parse_cmk_agent_ctl_status,
)
