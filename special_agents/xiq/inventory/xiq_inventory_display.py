
# -*- coding: utf-8 -*-
# Display specifications for ExtremeCloud IQ Inventory Tables

from cmk.gui.plugins.inventory import (
    inv_display,
    inv_table,
    inv_table_column,
)

# -------------------------
# ExtremeCloud IQ - APs
# -------------------------

inv_display.add_inventory_display(
    name="extreme_ap",
    title="ExtremeCloud IQ – Access Points",
    table=inv_table(
        columns=[
            inv_table_column("id",              title="ID"),
            inv_table_column("hostname",        title="Hostname"),
            inv_table_column("serial",          title="Serial"),
            inv_table_column("mac",             title="MAC"),
            inv_table_column("ip",              title="IP Address"),
            inv_table_column("model",           title="Model"),
            inv_table_column("software",        title="Software Version"),
            inv_table_column("location_full",   title="Location (full path)"),
            inv_table_column("location_leaf",   title="Location (short)"),
            inv_table_column("device_function", title="Device Function"),
        ],
    ),
)

# -------------------------
# ExtremeCloud IQ - Switches
# -------------------------

inv_display.add_inventory_display(
    name="extreme_sw",
    title="ExtremeCloud IQ – Switches",
    table=inv_table(
        columns=[
            inv_table_column("id",              title="ID"),
            inv_table_column("hostname",        title="Hostname"),
            inv_table_column("serial",          title="Serial"),
            inv_table_column("mac",             title="MAC"),
            inv_table_column("ip",              title="IP Address"),
            inv_table_column("model",           title="Model"),
            inv_table_column("software",        title="Software Version"),
            inv_table_column("location_full",   title="Location (full path)"),
            inv_table_column("location_leaf",   title="Location (short)"),
            inv_table_column("device_function", title="Device Function"),
        ],
    ),
)

# -------------------------
# ExtremeCloud IQ - Misc Devices
# -------------------------

inv_display.add_inventory_display(
    name="extreme_misc",
    title="ExtremeCloud IQ – Misc Devices",
    table=inv_table(
        columns=[
            inv_table_column("id",              title="ID"),
            inv_table_column("hostname",        title="Hostname"),
            inv_table_column("serial",          title="Serial"),
            inv_table_column("mac",             title="MAC"),
            inv_table_column("ip",              title="IP Address"),
            inv_table_column("model",           title="Model"),
            inv_table_column("software",        title="Software Version"),
            inv_table_column("location_full",   title="Location (full path)"),
            inv_table_column("location_leaf",   title="Location (short)"),
            inv_table_column("device_function", title="Device Function"),
        ],
    ),
)
