"""Shared geometry and thresholds for the DDROID water-point simulation.

Levels are fractions of each vessel. Switch thresholds match the SRS:
trough LOW / ADEQUATE / FULL, plus an independent high cutoff and a supply
low switch. Volumes are in litres so the animated Gazebo scene and the
controller stay in lockstep.
"""

SLICES = 16

TROUGH_LOW = 0.30
TROUGH_HIGH = 0.75
TROUGH_CUTOFF = 0.92
SUPPLY_LOW = 0.20

TROUGH_CAPACITY_L = 10.0
SUPPLY_CAPACITY_L = 18.0

PUMP_L_PER_S = 0.40
DRINK_L_PER_S = 0.32
MAX_RUN_S = 60.0
MANUAL_LIMIT_S = 15.0
SAMPLE_PERIOD_S = 1.0
DEBOUNCE_SAMPLES = 2

# Starts low in the trough, with enough supply for one full refill and a
# second refill that crosses the supply-low switch.
TROUGH_START_L = 1.2
SUPPLY_START_L = 12.3
SUPPLY_TOPUP_L = 14.0

SUPPLY = {
    "cx": -0.72,
    "cy": 0.0,
    "z0": 0.90,
    "sx": 0.30,
    "sy": 0.30,
    "h": 0.34,
}
TROUGH = {
    "cx": 0.62,
    "cy": 0.02,
    "z0": 0.84,
    "sx": 0.66,
    "sy": 0.32,
    "h": 0.16,
}

HIDDEN_Z = -4.0
PUMP_XYZ = (-0.05, 0.0, 0.98)
MODE_LAMP_XYZ = (0.0, -0.42, 0.82)


def fraction(volume_l, capacity_l):
    if capacity_l <= 0:
        return 0.0
    return max(0.0, min(1.0, volume_l / capacity_l))


def slice_pose(vessel, index, visible):
    """World pose for one water slice. Hidden slices park below the ground."""
    if not visible:
        return (vessel["cx"], vessel["cy"], HIDDEN_Z)
    step = vessel["h"] / SLICES
    z = vessel["z0"] + (index + 0.5) * step
    return (vessel["cx"], vessel["cy"], z)


def visible_slice_count(level_fraction):
    count = int(round(level_fraction * SLICES))
    return max(0, min(SLICES, count))


def switch_anchor(vessel, level_fraction, x_shift=0.0):
    z = vessel["z0"] + level_fraction * vessel["h"]
    y = vessel["cy"] - vessel["sy"] / 2.0 - 0.045
    x = vessel["cx"] + x_shift
    return (x, y, z)
