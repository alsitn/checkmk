#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Checkbox,
    Dictionary,
    Integer,
    Optional,
    TextAscii,
    Tuple,
)
from cmk.gui.plugins.wato import (
    RulespecGroupCheckParametersDiscovery,
    RulespecGroupCheckParametersStorage,
    register_check_parameters,
    register_rule,
)

register_rule(
    RulespecGroupCheckParametersDiscovery,
    varname="inventory_heartbeat_crm_rules",
    title=_("Heartbeat CRM Discovery"),
    valuespec=Dictionary(
        elements=[
            ("naildown_dc",
             Checkbox(
                 title=_("Naildown the DC"),
                 label=_("Mark the currently distinguished controller as preferred one"),
                 help=_(
                     "Nails down the DC to the node which is the DC during discovery. The check "
                     "will report CRITICAL when another node becomes the DC during later checks."))
            ),
            ("naildown_resources",
             Checkbox(
                 title=_("Naildown the resources"),
                 label=_("Mark the nodes of the resources as preferred one"),
                 help=_(
                     "Nails down the resources to the node which is holding them during discovery. "
                     "The check will report CRITICAL when another holds the resource during later checks."
                 ))),
        ],
        help=_('This rule can be used to control the discovery for Heartbeat CRM checks.'),
        optional_keys=[],
    ),
    match='dict',
)

register_check_parameters(
    RulespecGroupCheckParametersStorage,
    "heartbeat_crm",
    _("Heartbeat CRM general status"),
    Tuple(elements=[
        Integer(
            title=_("Maximum age"),
            help=_("Maximum accepted age of the reported data in seconds"),
            unit=_("seconds"),
            default_value=60,
        ),
        Optional(
            TextAscii(allow_empty=False),
            title=_("Expected DC"),
            help=_("The hostname of the expected distinguished controller of the cluster"),
        ),
        Optional(
            Integer(min_value=2, default_value=2),
            title=_("Number of Nodes"),
            help=_("The expected number of nodes in the cluster"),
        ),
        Optional(
            Integer(min_value=0,),
            title=_("Number of Resources"),
            help=_("The expected number of resources in the cluster"),
        ),
    ]),
    None,
    match_type="first",
)
