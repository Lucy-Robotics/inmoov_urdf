# InMoov i2 (this package)

## What this repository implements today

<<<<<<< HEAD
**`inmoov_urdf`** ships an **InMoov i1-line** robot description under `description/` (meshes, joints, ros2_control xacro). The hardware YAML in **`config/hardware/active.yaml`** therefore lists only actuators and sensors that match **that** URDF and the current Lucy wiring (arms, torso shoulder Y, fingers, pressure sensors, and so on).

It does **not** list **InMoov i2-style** head and expression actuators (extra eyelids, cheeks, brows, separate eyeball drivers, and so on) because those joints are either absent from the processed URDF or not yet committed to a single wiring story in this repo.

## Why keep talking about i2?

A future evolution might split or extend into an **`inmoov_i2`** description package with additional head DOFs. When that happens, the same **YAML schema** as `active.yaml` still applies: each new servo needs a row under **`actuators:`** with a **`urdf_joint`** that exactly matches the joint name in **`robot_description`**, plus board, pins, calibration, and limits.

This document is the **bridge**: it explains that gap and gives a **copy-paste-oriented appendix** in YAML form. Treat every **`urdf_joint`** in the appendix as **something you must reconcile** with the actual i2 (or extended i1) URDF-some entries use **current i1** head joint names where they exist; others use **placeholder** names for expression axes that the legacy xacro named differently from any joint in today’s URDF.
=======
**`inmoov_urdf`** ships the **InMoov i2** robot description under `description/robot_description/`, vendored from [Artur-Fedjukevits/inmoov_ros2](https://github.com/Artur-Fedjukevits/inmoov_ros2/tree/main/src/inmoov_description) (`src/inmoov_description`, commit `73c584b`). Mesh URIs were rewritten from `package://inmoov_description/meshes/` to the parent `mesh_dir`; `description/urdf/inmoov.urdf.xacro` adds a fixed `base_node` root above the i2 `stand_link`. Meshes are CC BY-NC 4.0 (see `description/robot_description/LICENSE-ASSETS.md`).

The hardware YAML in **`config/hardware/active.yaml`** maps the existing Lucy actuators (arms, torso, fingers, neck, jaw, eyes) onto i2 joint names. The i2 **expression** joints (eyelids, cheeks, brows, forehead, upper lip) exist in the URDF but are not wired yet: the generator publishes them at 0 through `joint_state_broadcaster` `extra_joints`.
>>>>>>> 3e4104f (feat(description): switch to the InMoov i2 model)

## How to add i2 head actuators to the YAML

1. **Freeze URDF joint names** in the description package (each DOF exactly one `joint name="..."` in the generated URDF).
2. For each servo on **`rp2040_torso_head`**, append one list element to **`actuators:`** in `active.yaml` (or a preset under `configs/`).
3. Assign **`virtual_pin`** as **contiguous integers per board**, starting after the last existing actuator on that board (today, shoulder Y uses `0` and `1` on `rp2040_torso_head`).
4. Set **`physical_pin`** to the PCA9685 channel (or equivalent) from your **actual** schematic. The appendix below uses **example** channels (jaw on **7**, cheeks **8-9**, and so on through **22**) typical of full InMoov-style head wiring. Many draft tables also put “head roll” on **physical_pin 6**, which **collides** with Lucy’s use of pins **5-6** for shoulder Y on `rp2040_torso_head`-treat the appendix as a **template**, then renumber every `physical_pin` to match the board you build.
5. Tune **`servo_*_rad`**, **`offset_rad`**, **`direction`**, and **`scale`** on the bench once the joint exists in ros2_control.

## Appendix - example YAML: i2-oriented head / expression actuators

Paste the list items at the end of the top-level **`actuators:`** sequence in `active.yaml` (or merge a preset) once the URDF exposes matching joints and each **`physical_pin`** is verified on the PCA.

**Pin conflict note:** If you follow common InMoov-style numbering, “head roll” often lands on **`physical_pin: 6`**, which collides with Lucy’s **`right_shoulder_y_joint`** on the same board (also pin **6**). The first row below uses **`physical_pin: 23`** as a stand-in for “move head roll to a free channel”; change it to match your PCB.

**`virtual_pin`:** Continue after the last actuator on `rp2040_torso_head` (today **`0`** and **`1`** for shoulder Y). The appendix uses **`2` … `18`**.

**`urdf_joint`:** every row matches a joint in the current `description/robot_description` tree.

```yaml
# Append under the top-level key `actuators:` (not as a nested document).
  - id: i2_head_roll_neck
    urdf_joint: neck_joint
    board: rp2040_torso_head
    virtual_pin: 2
    physical_pin: 23
    servo_type: "270"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 4.71239
    servo_default_rad: 2.35619
    enabled: false

  - id: i2_jaw
    urdf_joint: i02_head_jaw_joint
    board: rp2040_torso_head
    virtual_pin: 3
    physical_pin: 7
    servo_type: "300"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 2.61799
    servo_default_rad: 1.30900
    enabled: false

  - id: i2_left_cheek
    urdf_joint: i02_head_left_cheek_joint
    board: rp2040_torso_head
    virtual_pin: 4
    physical_pin: 8
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_cheek
    urdf_joint: i02_head_right_cheek_joint
    board: rp2040_torso_head
    virtual_pin: 5
    physical_pin: 9
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_upper_lip
    urdf_joint: i02_head_upper_lip_joint
    board: rp2040_torso_head
    virtual_pin: 6
    physical_pin: 10
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_upper_left_eyelid
    urdf_joint: i02_head_left_top_eyelid_joint
    board: rp2040_torso_head
    virtual_pin: 7
    physical_pin: 11
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_upper_right_eyelid
    urdf_joint: i02_head_right_top_eyelid_joint
    board: rp2040_torso_head
    virtual_pin: 8
    physical_pin: 12
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_lower_left_eyelid
    urdf_joint: i02_head_left_bottom_eyelid_joint
    board: rp2040_torso_head
    virtual_pin: 9
    physical_pin: 13
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_lower_right_eyelid
    urdf_joint: i02_head_right_bottom_eyelid_joint
    board: rp2040_torso_head
    virtual_pin: 10
    physical_pin: 14
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_eye_horizontal
    urdf_joint: i02_head_left_eye_horizontal_joint
    board: rp2040_torso_head
    virtual_pin: 11
    physical_pin: 15
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_eye_vertical
    urdf_joint: i02_head_left_eye_vertical_joint
    board: rp2040_torso_head
    virtual_pin: 12
    physical_pin: 16
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_eye_horizontal
    urdf_joint: i02_head_right_eye_horizontal_joint
    board: rp2040_torso_head
    virtual_pin: 13
    physical_pin: 17
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_eye_vertical
    urdf_joint: i02_head_right_eye_vertical_joint
    board: rp2040_torso_head
    virtual_pin: 14
    physical_pin: 18
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_eyebrow
    urdf_joint: i02_head_left_eyebrow_joint
    board: rp2040_torso_head
    virtual_pin: 15
    physical_pin: 19
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_eyebrow
    urdf_joint: i02_head_right_eyebrow_joint
    board: rp2040_torso_head
    virtual_pin: 16
    physical_pin: 20
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_forehead
    urdf_joint: i02_head_left_forehead_joint
    board: rp2040_torso_head
    virtual_pin: 17
    physical_pin: 21
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_forehead
    urdf_joint: i02_head_right_forehead_joint
    board: rp2040_torso_head
    virtual_pin: 18
    physical_pin: 22
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false
```

<<<<<<< HEAD
**Optional i1 head joints** not covered by the legacy expression block (add only if your URDF keeps them and you have servos): `i01.head.rothead_link_joint`, `i01.head.neck.001_link_joint`, `i01.head.eyeLeft_link_joint`, `i01.head.eyeRight_link_joint`, and the `*.001_link_joint` eye variants-each needs its own free **`physical_pin`** and next **`virtual_pin`**.

=======
>>>>>>> 3e4104f (feat(description): switch to the InMoov i2 model)
