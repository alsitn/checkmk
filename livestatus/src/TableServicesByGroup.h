// Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the
// terms and conditions defined in the file COPYING, which is part of this
// source code package.

#ifndef TableServicesByGroup_h
#define TableServicesByGroup_h

#include "config.h"  // IWYU pragma: keep

#include <string>

#include "Table.h"
class MonitoringCore;
class Query;

class TableServicesByGroup : public Table {
public:
    explicit TableServicesByGroup(MonitoringCore *mc);
    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::string namePrefix() const override;
    void answerQuery(Query *query) override;
    // NOTE: We do *not* implement findObject() here, because we don't know
    // which service group we should refer to: Every service can be part of many
    // service groups.
};

#endif  // TableServicesByGroup_h
