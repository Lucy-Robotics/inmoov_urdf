# Copyright 2025 Sentience Robotics Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Every actuated joint must declare a usable <limit> block."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from xacro_helper import run_xacro


def _paths():
    root = Path(__file__).resolve().parents[1]
    return (
        root / "description/urdf/inmoov.urdf.xacro",
        root / "description",
        root / "config/controllers.yaml",
        root / "config/hardware/active.yaml",
    )


def _expand_urdf() -> ET.Element:
    urdf_xacro, base, controllers, _ = _paths()
    r = run_xacro(
        [
            str(urdf_xacro),
            f"base_path:={base}",
            f"controller_config:={controllers}",
            "use_gazebo_sim:=false",
            "use_mock_hardware:=true",
        ]
    )
    assert r.returncode == 0, r.stderr + r.stdout
    return ET.fromstring(r.stdout)


@pytest.fixture(scope="module")
def urdf_root():
    return _expand_urdf()


@pytest.fixture(scope="module")
def actuated_joint_names():
    _, _, _, active = _paths()
    data = yaml.safe_load(active.read_text(encoding="utf-8"))
    return {a["urdf_joint"] for a in data["actuators"]}


def test_actuated_joints_have_limits(urdf_root, actuated_joint_names):
    """Each actuated joint must have a <limit> with non-degenerate bounds."""
    found: set[str] = set()
    for joint in urdf_root.findall("joint"):
        name = joint.get("name")
        if name not in actuated_joint_names:
            continue
        found.add(name)
        limit = joint.find("limit")
        assert limit is not None, f"missing <limit> on actuated joint {name}"
        lower = float(limit.get("lower"))
        upper = float(limit.get("upper"))
        assert upper > lower, f"{name} has degenerate limit lower={lower} upper={upper}"
        for attr in ("effort", "velocity"):
            assert float(limit.get(attr)) > 0, f"{name} non-positive {attr}"
    missing = actuated_joint_names - found
    assert not missing, f"actuators in active.yaml not present in URDF: {sorted(missing)}"


def test_model_scale_property_resolves(urdf_root):
    """Xacro should fully expand model_scale (no leftover ${...} tokens)."""
    text = ET.tostring(urdf_root, encoding="unicode")
    assert "${model_scale" not in text, "model_scale property left unevaluated"


def _urdf_limits(urdf_root) -> dict[str, tuple[float, float]]:
    return {
        j.get("name"): (float(j.find("limit").get("lower")), float(j.find("limit").get("upper")))
        for j in urdf_root.findall("joint")
        if j.find("limit") is not None
    }


def _off(value, expected) -> bool:
    return abs(float(value) - expected) > 1e-4


def test_hardware_limits_match_urdf_limits(urdf_root):
    """The servo travel in active.yaml must map onto exactly the URDF joint range."""
    _, _, _, active = _paths()
    actuators = yaml.safe_load(active.read_text(encoding="utf-8"))["actuators"]
    urdf_limits = _urdf_limits(urdf_root)
    mismatched = []
    for a in actuators:
        k = float(a["direction"]) * float(a["scale"])
        joint_range = sorted(
            (float(a[key]) - float(a["offset"])) * k for key in ("limit_min", "limit_max")
        )
        lower, upper = urdf_limits[a["urdf_joint"]]
        if abs(joint_range[0] - lower) > 1e-3 or abs(joint_range[1] - upper) > 1e-3:
            mismatched.append(f"{a['id']}: hardware {joint_range} vs URDF [{lower}, {upper}]")
    assert not mismatched, "\n".join(mismatched)


def test_ros2_control_command_ranges_match_urdf_limits(urdf_root):
    """The generated command_interface min/max must follow the URDF joint limits."""
    description = Path(__file__).resolve().parents[1] / "description"
    text = (description / "ros2_control/inmoov_ros2_control.xacro").read_text(encoding="utf-8")
    urdf_limits = _urdf_limits(urdf_root)
    pattern = re.compile(
        r'<joint name="([^"]+)">.*?<param name="min">([^<]+)</param>\s*'
        r'<param name="max">([^<]+)</param>',
        re.S,
    )
    mismatched = [
        f"{name}: command [{lo}, {hi}] vs URDF {urdf_limits[name]}"
        for name, lo, hi in pattern.findall(text)
        if _off(lo, urdf_limits[name][0]) or _off(hi, urdf_limits[name][1])
    ]
    assert not mismatched, "\n".join(mismatched)
