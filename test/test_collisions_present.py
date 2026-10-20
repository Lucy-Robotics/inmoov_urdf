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

"""i2 collision model: body and hand links carry collision geometry (mesh or primitive)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from xacro_helper import run_xacro

# Body links (Gazebo: self_collide=false).
BODY_LINKS = [
    "stand_link",
    "torso_bottom_link",
    "torso_z_link",
    "torso_y_link",
    "left_shoulder_x_link",
    "left_shoulder_z_link",
    "left_elbow_x_link",
    "left_wrist_z_link",
    "right_shoulder_x_link",
    "right_shoulder_z_link",
    "right_elbow_x_link",
    "right_wrist_z_link",
    "neck_link",
    "NewHead_origin",
    "i02_head_jaw",
]

# Upstream i2 ships these without collision geometry; listed so the gap stays visible.
KNOWN_NO_COLLISION = ["left_shoulder_y_link", "right_shoulder_y_link"]

# Hand links (Gazebo: self_collide=true, high mu); the palm is part of *_wrist_z_link.
HAND_LINKS = [
    f"i02_{side}Hand_{finger}{part}"
    for side in ("left", "right")
    for finger in ("index", "majeure", "ringFinger", "pinky")
    for part in ("Phal", "Mid", "Tip")
] + [
    f"i02_{side}Hand_Thumb{part}"
    for side in ("left", "right")
    for part in ("Mid", "Tip")
]


def _expand_urdf() -> ET.Element:
    root = Path(__file__).resolve().parents[1]
    r = run_xacro(
        [
            str(root / "description/urdf/inmoov.urdf.xacro"),
            f"base_path:={root / 'description'}",
            f"controller_config:={root / 'config/controllers.yaml'}",
            "use_gazebo_sim:=false",
            "use_mock_hardware:=true",
        ]
    )
    assert r.returncode == 0, r.stderr + r.stdout
    return ET.fromstring(r.stdout)


@pytest.fixture(scope="module")
def urdf_root():
    return _expand_urdf()


def _link(urdf_root: ET.Element, link_name: str) -> ET.Element | None:
    for link in urdf_root.findall("link"):
        if link.get("name") == link_name:
            return link
    return None


@pytest.mark.parametrize("name", BODY_LINKS + HAND_LINKS)
def test_link_has_collision(urdf_root, name):
    link = _link(urdf_root, name)
    assert link is not None, f"{name} missing from URDF"
    assert link.find("collision") is not None, f"{name} missing collision"


@pytest.mark.parametrize("name", KNOWN_NO_COLLISION)
def test_known_gap_still_exists(urdf_root, name):
    """Fails once upstream adds the collision: move the link into BODY_LINKS then."""
    link = _link(urdf_root, name)
    assert link is not None, f"{name} missing from URDF"
    assert link.find("collision") is None
