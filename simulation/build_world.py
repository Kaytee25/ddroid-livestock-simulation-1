"""Write the Gazebo world for the DDROID livestock water point."""

import os

from ddroid_scene import (
    MODE_LAMP_XYZ,
    PUMP_XYZ,
    SLICES,
    SUPPLY,
    SUPPLY_LOW,
    TROUGH,
    TROUGH_CUTOFF,
    TROUGH_HIGH,
    TROUGH_LOW,
    slice_pose,
    switch_anchor,
)

WORLD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds", "ddroid_water_point.sdf")

PLASTIC = (0.62, 0.66, 0.70, 1.0)
PLASTIC_DARK = (0.28, 0.32, 0.36, 1.0)
WATER = (0.12, 0.45, 0.82, 0.95)
WOOD = (0.45, 0.30, 0.16, 1.0)
GROUND = (0.36, 0.46, 0.28, 1.0)
COW = (0.42, 0.28, 0.16, 1.0)
COW_DARK = (0.22, 0.14, 0.08, 1.0)
WET = (0.10, 0.35, 0.85, 1.0)
DRY = (0.75, 0.75, 0.72, 1.0)
CUTOFF_WET = (0.85, 0.15, 0.12, 1.0)
PUMP_BODY = (0.15, 0.16, 0.18, 1.0)
LAMP_ON = (0.95, 0.55, 0.05, 1.0)
LAMP_OFF = (0.25, 0.25, 0.25, 1.0)
MODE_COLOURS = {
    "stopped": (0.45, 0.45, 0.45, 1.0),
    "idle": (0.15, 0.65, 0.25, 1.0),
    "refilling": (0.10, 0.35, 0.90, 1.0),
    "manual": (0.90, 0.70, 0.10, 1.0),
    "fault": (0.85, 0.12, 0.10, 1.0),
}


def _fmt(values):
    return " ".join(f"{value:.4f}" for value in values)


def _material(rgba):
    r, g, b, a = rgba
    return (
        "<material>"
        f"<ambient>{r} {g} {b} {a}</ambient>"
        f"<diffuse>{r} {g} {b} {a}</diffuse>"
        f"<specular>0.15 0.15 0.15 {a}</specular>"
        "</material>"
    )


def static_box(name, center, size, rgba, collision=True, movable=False):
    collision_xml = ""
    if collision:
        collision_xml = (
            '<collision name="collision"><geometry><box>'
            f"<size>{_fmt(size)}</size></box></geometry></collision>"
        )
    static_xml = "<static>true</static>"
    motion_xml = ""
    if movable:
        static_xml = "<static>false</static>"
        motion_xml = """
        <kinematic>true</kinematic>
        <gravity>false</gravity>
        <inertial>
          <mass>0.05</mass>
          <inertia>
            <ixx>0.0001</ixx><ixy>0</ixy><ixz>0</ixz>
            <iyy>0.0001</iyy><iyz>0</iyz><izz>0.0001</izz>
          </inertia>
        </inertial>"""
    return f"""
    <model name="{name}">
      {static_xml}
      <pose>{_fmt(center)} 0 0 0</pose>
      <link name="link">{motion_xml}
        <visual name="visual">
          <geometry><box><size>{_fmt(size)}</size></box></geometry>
          {_material(rgba)}
        </visual>
        {collision_xml}
      </link>
    </model>"""


def static_sphere(name, center, radius, rgba, movable=False):
    static_xml = "<static>true</static>"
    motion_xml = ""
    if movable:
        static_xml = "<static>false</static>"
        motion_xml = """
        <kinematic>true</kinematic>
        <gravity>false</gravity>
        <inertial>
          <mass>0.02</mass>
          <inertia>
            <ixx>0.0001</ixx><ixy>0</ixy><ixz>0</ixz>
            <iyy>0.0001</iyy><iyz>0</iyz><izz>0.0001</izz>
          </inertia>
        </inertial>"""
    return f"""
    <model name="{name}">
      {static_xml}
      <pose>{_fmt(center)} 0 0 0</pose>
      <link name="link">{motion_xml}
        <visual name="visual">
          <geometry><sphere><radius>{radius:.4f}</radius></sphere></geometry>
          {_material(rgba)}
        </visual>
      </link>
    </model>"""


def static_cylinder(name, center, radius, length, rgba):
    return f"""
    <model name="{name}">
      <static>true</static>
      <pose>{_fmt(center)} 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry><cylinder><radius>{radius:.4f}</radius><length>{length:.4f}</length></cylinder></geometry>
          {_material(rgba)}
        </visual>
        <collision name="collision">
          <geometry><cylinder><radius>{radius:.4f}</radius><length>{length:.4f}</length></cylinder></geometry>
        </collision>
      </link>
    </model>"""


def vessel(prefix, spec, wall_h, rgba):
    """Open-top tank. The near wall is lower so the water surface stays visible."""
    wall = 0.018
    cx, cy, z0 = spec["cx"], spec["cy"], spec["z0"]
    sx, sy = spec["sx"], spec["sy"]
    parts = []
    parts.append(
        static_box(
            f"{prefix}_floor",
            (cx, cy, z0 - wall / 2),
            (sx + 2 * wall, sy + 2 * wall, wall),
            rgba,
        )
    )
    side_z = z0 + wall_h / 2
    side_h = wall_h
    parts.append(
        static_box(
            f"{prefix}_wall_left",
            (cx - sx / 2 - wall / 2, cy, side_z),
            (wall, sy, side_h),
            rgba,
        )
    )
    parts.append(
        static_box(
            f"{prefix}_wall_right",
            (cx + sx / 2 + wall / 2, cy, side_z),
            (wall, sy, side_h),
            rgba,
        )
    )
    parts.append(
        static_box(
            f"{prefix}_wall_back",
            (cx, cy + sy / 2 + wall / 2, side_z),
            (sx + 2 * wall, wall, side_h),
            rgba,
        )
    )
    lip = wall_h * 0.42
    parts.append(
        static_box(
            f"{prefix}_wall_front",
            (cx, cy - sy / 2 - wall / 2, z0 + lip / 2),
            (sx + 2 * wall, wall, lip),
            rgba,
        )
    )
    return "\n".join(parts)


def water_slices(prefix, vessel_spec):
    step = vessel_spec["h"] / SLICES
    thickness = step * 0.92
    size = (vessel_spec["sx"] * 0.96, vessel_spec["sy"] * 0.96, thickness)
    parts = []
    for index in range(SLICES):
        center = slice_pose(vessel_spec, index, visible=False)
        parts.append(
            static_box(
                f"{prefix}_water_{index:02d}",
                center,
                size,
                WATER,
                collision=False,
                movable=True,
            )
        )
    return "\n".join(parts)


def marker_pair(name, anchor, wet_rgba, dry_rgba, radius=0.022):
    hidden = (anchor[0], anchor[1], -4.0)
    return "\n".join(
        [
            static_sphere(f"{name}_wet", hidden, radius, wet_rgba, movable=True),
            static_sphere(f"{name}_dry", anchor, radius, dry_rgba, movable=True),
        ]
    )


def livestock(name, origin, yaw_note):
    """A simple standing animal built from boxes, facing the trough."""
    del yaw_note
    x, y, z = origin
    body = static_box(f"{name}_body", (x, y, z + 0.16), (0.34, 0.16, 0.16), COW)
    head = static_box(f"{name}_head", (x + 0.20, y, z + 0.22), (0.12, 0.10, 0.12), COW_DARK)
    legs = []
    for index, (dx, dy) in enumerate(((-0.10, -0.05), (-0.10, 0.05), (0.10, -0.05), (0.10, 0.05))):
        legs.append(
            static_box(
                f"{name}_leg_{index}",
                (x + dx, y + dy, z + 0.06),
                (0.04, 0.04, 0.12),
                COW_DARK,
            )
        )
    return "\n".join([body, head, *legs])


def table():
    top = static_box("bench_top", (0.0, 0.0, 0.74), (2.15, 1.15, 0.06), WOOD)
    legs = []
    for index, (x, y) in enumerate(((-0.95, -0.45), (-0.95, 0.45), (0.95, -0.45), (0.95, 0.45))):
        legs.append(static_cylinder(f"bench_leg_{index}", (x, y, 0.36), 0.035, 0.72, PLASTIC_DARK))
    return "\n".join([top, *legs])


def pipes():
    supply_x = SUPPLY["cx"] + SUPPLY["sx"] / 2
    trough_x = TROUGH["cx"] - TROUGH["sx"] / 2
    mid_x = (supply_x + trough_x) / 2
    z = 0.96
    horizontal = static_box(
        "pipe_horizontal",
        (mid_x, 0.0, z),
        (trough_x - supply_x, 0.03, 0.03),
        PLASTIC_DARK,
    )
    return horizontal


def world_xml():
    hidden_mode = (MODE_LAMP_XYZ[0], MODE_LAMP_XYZ[1], -4.0)
    mode_lamps = []
    for name, rgba in MODE_COLOURS.items():
        center = MODE_LAMP_XYZ if name == "stopped" else hidden_mode
        mode_lamps.append(static_sphere(f"mode_{name}", center, 0.045, rgba, movable=True))

    pump_lamp_off = static_sphere(
        "pump_lamp_off",
        (PUMP_XYZ[0], PUMP_XYZ[1], PUMP_XYZ[2] + 0.10),
        0.03,
        LAMP_OFF,
        movable=True,
    )
    pump_lamp_on = static_sphere(
        "pump_lamp_on",
        (PUMP_XYZ[0], PUMP_XYZ[1], -4.0),
        0.03,
        LAMP_ON,
        movable=True,
    )

    switches = "\n".join(
        [
            marker_pair("supply_low", switch_anchor(SUPPLY, SUPPLY_LOW), WET, DRY),
            marker_pair("trough_low", switch_anchor(TROUGH, TROUGH_LOW, x_shift=-0.18), WET, DRY),
            marker_pair("trough_high", switch_anchor(TROUGH, TROUGH_HIGH, x_shift=0.05), WET, DRY),
            marker_pair(
                "trough_cutoff",
                switch_anchor(TROUGH, TROUGH_CUTOFF, x_shift=0.22),
                CUTOFF_WET,
                DRY,
                radius=0.026,
            ),
        ]
    )

    return f"""<?xml version="1.0" ?>
<sdf version="1.9">
  <world name="ddroid">
    <gravity>0 0 -9.8</gravity>
    <physics name="ddroid_physics" type="ignored">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.9 0.9 0.82 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.35 0.25 -1</direction>
    </light>
    <scene>
      <ambient>0.45 0.48 0.5 1</ambient>
      <background>0.62 0.76 0.88 1</background>
      <grid>false</grid>
    </scene>

    <model name="ground">
      <static>true</static>
      <pose>0 0 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>20 20</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>12 12</size></plane></geometry>
          {_material(GROUND)}
        </visual>
      </link>
    </model>

    {table()}
    {static_box("supply_stand", (SUPPLY["cx"], SUPPLY["cy"], 0.83), (0.22, 0.22, 0.12), WOOD)}
    {vessel("supply", SUPPLY, SUPPLY["h"] + 0.04, PLASTIC)}
    {vessel("trough", TROUGH, TROUGH["h"] + 0.03, PLASTIC)}
    {pipes()}
    {static_cylinder("pump_body", PUMP_XYZ, 0.055, 0.14, PUMP_BODY)}
    {pump_lamp_off}
    {pump_lamp_on}
    {"".join(mode_lamps)}
    {water_slices("supply", SUPPLY)}
    {water_slices("trough", TROUGH)}
    {switches}
    {livestock("animal_a", (0.35, -0.48, 0.77), 0.0)}
    {livestock("animal_b", (0.78, -0.50, 0.77), 0.0)}

    <model name="overview_camera">
      <static>true</static>
      <pose>1.60 -2.10 1.70 0 -0.28 2.22</pose>
      <link name="link">
        <sensor name="camera" type="camera">
          <always_on>1</always_on>
          <update_rate>4</update_rate>
          <visualize>false</visualize>
          <topic>overview</topic>
          <camera>
            <horizontal_fov>1.15</horizontal_fov>
            <image>
              <width>960</width>
              <height>540</height>
              <format>R8G8B8</format>
            </image>
            <clip>
              <near>0.1</near>
              <far>40</far>
            </clip>
          </camera>
        </sensor>
      </link>
    </model>
  </world>
</sdf>
"""


def main():
    os.makedirs(os.path.dirname(WORLD_PATH), exist_ok=True)
    xml = world_xml()
    with open(WORLD_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(xml)
    print(WORLD_PATH)


if __name__ == "__main__":
    main()
