

# Planar Linkage JSON Schema & OOP Toolkit

This repository provides:
- A **JSON schema** for describing arbitrary planar mechanisms
- A fully object-oriented Python package (`Linkage2D` and related classes) for loading, solving, visualizing, and animating mechanisms
- A CLI (`linkage_tools.py`) for validation, solving, visualization, and animation (including OOP-based animation)

All features are available both via the CLI and the OOP Python API.

---

## � OOP Workflow Overview

The core of this toolkit is the `Linkage2D` class, which mirrors the JSON schema and provides methods for:
- Loading mechanisms from JSON (`Linkage2D.from_json`)
- Solving the constraint closure problem (`linkage.solve_linkage()`)
- Visualizing and animating mechanisms (see `plot_linkage2d`, `animate_linkage2d`)

All joint types are fully supported: **revolute**, **prismatic**, **pin-in-slot**, **gear**, and **weld**.

---

## 🖥️ Usage: Python CLI & OOP API

### CLI Commands

```bash
python linkage_tools.py validate <schema.json> <mechanism.json>   # Validate against schema
python linkage_tools.py visualize <mechanism.json>                # Static plot
python linkage_tools.py solve_and_plot <mechanism.json>           # Solve and plot configuration
python linkage_tools.py animate <mechanism.json>                  # Animate (legacy, procedural)
python linkage_tools.py animate2d <mechanism.json>                # Animate (OOP, recommended)
```

### OOP Python API Example

```python
from planar_linkage.linkage2d import Linkage2D
import matplotlib.pyplot as plt
import json

# Load mechanism from JSON
with open('four_bar.json') as f:
  data = json.load(f)
linkage = Linkage2D.from_json(data)

# Solve the linkage
linkage.solve_linkage()

# Visualize
from linkage_tools import plot_linkage2d
plot_linkage2d(linkage)
plt.show()

# Animate (see linkage_tools.py for animate_linkage2d)
```

---

## 📐 Coordinate Conventions

- **Global frame**: +X right, +Y up, counterclockwise angles are positive.
- **Link-local frame**: Each link has its own coordinate system. All geometry (`points`, `directions`, `lines`, `circles`, `arcs`) is expressed in this local frame.
- **Pose**: `pose.position` and `pose.angle` define the transform from link-local to the global frame.



## 🔗 Link Definition

A `link` entry contains:

| Field        | Description |
|--------------|-------------|
| `id`         | Link identifier (string) |
| `name`       | Human-readable link name |
| `isGrounded` | `true` if the link is fixed in the ground frame |
| `pose`       | Position `[x, y]` and orientation `angle` in **global** coordinates |
| `points`     | List of points fixed on the link |
| `directions` | List of direction vectors fixed on the link (angle in link-local frame) |
| `lines`      | Lines fixed on the link, defined by two point IDs |
| `circles`    | Circles fixed on the link (with `center_point_id` and `radius`) |
| `arcs`       | Arcs fixed on the link |

### Example Link with All Geometry Types

```json
{
  "id": "L1",
  "name": "ground",
  "isGrounded": true,
  "pose": { "position": [0, 0], "angle": 0 },
  "points": [
    { "id": "A", "name": "A", "position": [0, 0] },
    { "id": "D", "name": "D", "position": [300, 0] }
  ],
  "directions": [
    { "id": "ax0", "name": "x_axis", "angle": 0 }
  ],
  "lines": [
    { "id": "AD", "name": "AD", "point_ids": ["A", "D"] }
  ],
  "circles": [
    { "id": "cA", "name": "A_bearing", "center_point_id": "A", "radius": 8 }
  ],
  "arcs": [
    {
      "id": "arcDemo",
      "name": "decor",
      "center_point_id": "A",
      "radius": 40,
      "start_angle": 0,
      "end_angle": 90,
      "direction": "ccw"
    }
  ]
}
```

---

## ⚙️ Joint Types

Each joint connects a **parent** link to a **child** link.

### 1. Revolute (R)

```json
{
  "id": "R1",
  "name": "A_rev",
  "type": "revolute",
  "parent": "L1", "point_id_parent": "A",
  "child":  "L2", "point_id_child":  "A2"
}
```

**Definition:** The point `A` on `L1` coincides with `A2` on `L2`.

---

### 2. Prismatic (P)

```json
{
  "id": "P1",
  "name": "Slider",
  "type": "prismatic",
  "parent": "L1",
  "axis_parent": { "point_id": "D", "direction_id": "ax0" },
  "child":  "L3",
  "point_id_child": "S",
  "limits": { "min": -50, "max": 350 }
}
```

**Definition:** The point `S` on `L3` slides along the axis defined by point `D` and direction `ax0` on `L1`.

---

### 3. Pin-in-slot

```json
{
  "id": "PS1",
  "name": "SlotJoint",
  "type": "pin-in-slot",
  "parent": "L1",
  "line_id_parent": "AD",
  "child": "L3",
  "point_id_child": "Pslot"
}
```

**Definition:** Point `Pslot` on `L3` moves along the line `AD` on `L1`.

---

### 4. Gear

```json
{
  "id": "G1",
  "name": "GearPair",
  "type": "gear",
  "parent": "L2",
  "child":  "L4",
  "ratio": -2.0,
  "phase_offset": 0.0
}
```

**Definition:** The angle of `L2` = `ratio` × angle of `L4` + `phase_offset`. Negative ratio for external mesh.

---

### 5. Weld

```json
{
  "id": "W1",
  "name": "WeldedLink",
  "type": "weld",
  "parent": "L1",
  "child":  "L3",
  "relative_pose": { "position": [10, 10], "angle": 90.0 }
}
```

**Definition:** `L3` is fixed rigidly to `L1` with a constant relative pose (position and angle) in the parent link's frame.

---


## 📂 Example Mechanisms

The following example JSON files are included and schema-compliant:
- `four_bar.json` (four-bar linkage)
- `crank_slider.json` (slider-crank)
- `crank_pin_in_slot.json` (crank-slider with slot)
- `four_bar_weld.json` (four-bar with welded link and circle)


### A. Planar Four-Bar

- Links: Ground, Input, Coupler, Output
- Joints: 4 × revolute

```json
{
  "links": [
    { "id": "L1", "name": "ground", "isGrounded": true, "pose": { "position": [0,0], "angle": 0 }, "points": [], "directions": [], "lines": [], "circles": [], "arcs": [] },
    { "id": "L2", "name": "input",  "isGrounded": false, "pose": { "position": [0,0], "angle": 0 }, "points": [], "directions": [], "lines": [], "circles": [], "arcs": [] },
    { "id": "L3", "name": "coupler", "isGrounded": false, "pose": { "position": [0,0], "angle": 0 }, "points": [], "directions": [], "lines": [], "circles": [], "arcs": [] },
    { "id": "L4", "name": "output",  "isGrounded": false, "pose": { "position": [0,0], "angle": 0 }, "points": [], "directions": [], "lines": [], "circles": [], "arcs": [] }
  ],
  "joints": [
    { "id": "R1", "type": "revolute", "parent": "L1", "point_id_parent": "A", "child": "L2", "point_id_child": "A2" },
    { "id": "R2", "type": "revolute", "parent": "L2", "point_id_parent": "B", "child": "L3", "point_id_child": "B3" },
    { "id": "R3", "type": "revolute", "parent": "L3", "point_id_parent": "C", "child": "L4", "point_id_child": "C4" },
    { "id": "R4", "type": "revolute", "parent": "L1", "point_id_parent": "D", "child": "L4", "point_id_child": "D4" }
  ]
}
```

---

### B. Slider-Crank

- Links: Ground, Crank, Connecting Rod, Slider
- Joints: Revolute, Revolute, Prismatic

```json
"joints": [
  { "id": "R1", "type": "revolute", "parent": "L_ground", "point_id_parent": "A", "child": "L_crank", "point_id_child": "A2" },
  { "id": "R2", "type": "revolute", "parent": "L_crank", "point_id_parent": "B", "child": "L_rod", "point_id_child": "B2" },
  { "id": "P1", "type": "prismatic", "parent": "L_ground", "axis_parent": { "point_id": "D", "direction_id": "ax0" }, "child": "L_slider", "point_id_child": "S" }
]
```

---

### C. Five-Bar

- Links: Ground, Input1, Input2, Coupler1, Coupler2
- Joints: 5 × revolute

```json
"joints": [
  { "id": "R1", "type": "revolute", "parent": "G", "point_id_parent": "A", "child": "I1", "point_id_child": "A1" },
  { "id": "R2", "type": "revolute", "parent": "I1", "point_id_parent": "B1", "child": "C1", "point_id_child": "B" },
  { "id": "R3", "type": "revolute", "parent": "G", "point_id_parent": "D", "child": "I2", "point_id_child": "D2" },
  { "id": "R4", "type": "revolute", "parent": "I2", "point_id_parent": "C2", "child": "C2L", "point_id_child": "C" },
  { "id": "R5", "type": "revolute", "parent": "C1", "point_id_parent": "E1", "child": "C2L", "point_id_child": "E2" }
]
```

---

### D. Geared Five-Bar

- Same as five-bar, plus a gear constraint between Input1 and Input2:

```json
{ "id": "G1", "type": "gear", "parent": "I1", "child": "I2", "ratio": -1, "phase_offset": 0 }
```

---


## 📏 Validation

You can validate any mechanism JSON file using the CLI or directly with Python and the provided schema:

```bash
pip install jsonschema
```

```python
import json
import jsonschema

with open("planar_linkage.schema.json") as f:
    schema = json.load(f)

with open("my_linkage.json") as f:
    data = json.load(f)

jsonschema.validate(instance=data, schema=schema)
print("Valid JSON linkage!")
```

Or use the CLI:
```bash
python linkage_tools.py validate my_linkage.json
```

---


## 📜 License

MIT License. See [LICENSE](LICENSE) file.
