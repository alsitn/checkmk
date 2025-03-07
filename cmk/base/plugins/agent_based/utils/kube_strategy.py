#!/usr/bin/env python3
# -*- coding: utf-8 -*
# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Union

from cmk.base.plugins.agent_based.utils.kube import (
    OnDelete,
    Recreate,
    RollingUpdate,
    StatefulSetRollingUpdate,
)


def strategy_text(strategy: Union[RollingUpdate, Recreate, OnDelete]) -> str:
    """Used for Deployment and DaemonSet"""

    if isinstance(strategy, RollingUpdate):
        return (
            f"{strategy.type_} "
            f"(max surge: {strategy.max_surge}, "
            f"max unavailable: {strategy.max_unavailable})"
        )
    return strategy.type_


def statefulset_strategy_text(strategy: Union[StatefulSetRollingUpdate, OnDelete]) -> str:
    if isinstance(strategy, StatefulSetRollingUpdate):
        return f"{strategy.type_} (partitioned at: {strategy.partition})"
    return strategy.type_
