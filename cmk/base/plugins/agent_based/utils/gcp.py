#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import json
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Mapping, Sequence

from google.cloud.asset_v1 import Asset
from google.cloud.monitoring_v3.types import TimeSeries

from ..agent_based_api.v1 import check_levels, check_levels_predictive
from ..agent_based_api.v1.type_defs import CheckResult, StringTable


@dataclass(frozen=True)
class GCPResult:
    ts: TimeSeries

    @classmethod
    def deserialize(cls, data: str) -> "GCPResult":
        ts = TimeSeries.from_json(data)
        return cls(ts=ts)


@dataclass(frozen=True)
class GCPAsset:
    asset: Asset

    @classmethod
    def deserialize(cls, data: str) -> "GCPAsset":
        return cls(asset=Asset.from_json(data))


@dataclass(frozen=True)
class SectionItem:
    rows: Sequence[GCPResult]


Section = Mapping[str, SectionItem]


@dataclass(frozen=True)
class AssetSection:
    project: str
    assets: Sequence[GCPAsset]

    def __iter__(self) -> Iterator[GCPAsset]:
        return iter(self.assets)


def parse_gcp(
    string_table: StringTable, label_key: str, extract: Callable[[str], str] = lambda x: x
) -> Section:
    rows = [GCPResult.deserialize(row[0]) for row in string_table]
    items = {row.ts.resource.labels[label_key] for row in rows}
    return {
        extract(item): SectionItem([r for r in rows if r.ts.resource.labels[label_key] == item])
        for item in items
    }


def parse_assets(string_table: StringTable) -> AssetSection:
    info = json.loads(string_table[0][0])
    project = info["project"]
    assets = [GCPAsset.deserialize(row[0]) for row in string_table[1:]]
    return AssetSection(project, assets)


@dataclass(frozen=True)
class MetricSpec:
    metric_type: str
    render_func: Callable
    scale: float = 1.0
    # TODO: use enum
    dtype: str = "float"


def _get_value(results: Sequence[GCPResult], spec: MetricSpec) -> float:
    # GCP does not always deliver all metrics. i.e. api/request_count only contains values if
    # api requests have occured. To ensure all metrics are displayed in check mk we default to
    # 0 in the absence of data.
    try:
        result = next(r for r in results if r.ts.metric.type == spec.metric_type)
        proto_value = result.ts.points[0].value
        if spec.dtype == "float":
            value = proto_value.double_value
        elif spec.dtype == "int":
            value = proto_value.int64_value
        else:
            raise NotImplementedError("unkown dtype")
        return value * spec.scale
    except StopIteration:
        return 0


def generic_check(
    metrics: Mapping[str, MetricSpec], timeseries: Sequence[GCPResult], params: Mapping[str, Any]
) -> CheckResult:
    for metric_name, metric_spec in metrics.items():
        value = _get_value(timeseries, metric_spec)
        levels_upper = params.get(metric_name)
        if isinstance(levels_upper, dict):
            yield from check_levels_predictive(
                value,
                metric_name=metric_name,
                render_func=metric_spec.render_func,
                levels=levels_upper,
            )
        else:
            yield from check_levels(
                value,
                metric_name=metric_name,
                render_func=metric_spec.render_func,
                levels_upper=levels_upper,
            )
