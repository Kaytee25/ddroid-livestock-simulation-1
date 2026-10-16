"""Headless check of the DDROID demonstration sequence."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ddroid_control import Controller, Plant
from ddroid_demo import run_demo


def main():
    plant = Plant()
    low, high, source, cutoff = plant.raw_switches()
    ctl = Controller(low, high, source, cutoff)
    assert ctl.mode == "STOPPED" and ctl.pump is False

    kinds, story = run_demo(plant, ctl, view=None, dt=0.1, realtime=False, hold_s=0.2)
    text = "\n".join(story)
    assert "reset while supply is low" in text
    assert "HIGH CUTOFF" in text
    assert "Demonstration complete" in text

    assert "armed_refill" in kinds
    assert kinds.count("full_stop") >= 2
    assert "fault" in kinds
    faults = [event["fault"] for event in ctl.events if event["kind"] == "fault"]
    assert "LOW SUPPLY" in faults
    assert "HIGH CUTOFF" in faults
    assert "reset" in kinds
    assert ctl.mode == "IDLE"
    assert ctl.pump is False
    assert ctl.fault is None

    # ADEQUATE must not start the pump. Drinking from mid-level stays IDLE
    # until the debounced state is LOW.
    hold = Plant()
    hold.trough_l = 6.0
    hold.supply_l = 15.0
    hold_ctl = Controller(True, False, True, False)
    hold_ctl.mode = "IDLE"
    for _ in range(80):
        hold_ctl.step(0.1, *hold.raw_switches())
        hold.step(0.1, hold_ctl.pump)
        assert hold_ctl.mode == "IDLE", hold_ctl.trough_state()
        assert hold_ctl.pump is False
    assert hold_ctl.trough_state() == "ADEQUATE"
    assert hold.trough_l > 3.0

    print("Control demonstration checks passed.")
    print("Events:", ", ".join(kinds))


if __name__ == "__main__":
    main()
