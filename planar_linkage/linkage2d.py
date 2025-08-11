
"""
Classes for 2D linkage mechanisms, matching the JSON schema structure.
"""
from typing import List, Optional, Dict, Any
import numpy as np
from scipy.optimize import least_squares
import math

class Link2D:
    def __init__(self, id: str, name: str = "", isGrounded: bool = False, pose: Optional[dict] = None,
                 points: Optional[List[dict]] = None, directions: Optional[List[dict]] = None,
                 lines: Optional[List[dict]] = None, circles: Optional[List[dict]] = None, arcs: Optional[List[dict]] = None):
        self.id = id
        self.name = name
        self.isGrounded = isGrounded
        self.pose = pose or {"position": [0, 0], "angle": 0}
        self.points = points or []
        self.directions = directions or []
        self.lines = lines or []
        self.circles = circles or []
        self.arcs = arcs or []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "isGrounded": self.isGrounded,
            "pose": self.pose,
            "points": self.points,
            "directions": self.directions,
            "lines": self.lines,
            "circles": self.circles,
            "arcs": self.arcs
        }

class Joint:
    def __init__(self, id: str, name: str, type: str, parent: str, child: str):
        self.id = id
        self.name = name
        self.type = type
        self.parent = parent
        self.child = child

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "parent": self.parent,
            "child": self.child
        }

class RevoluteJoint(Joint):
    def constraint_equation(self, links_by_id, unit_angle):
        parent = links_by_id[self.parent]
        child = links_by_id[self.child]
        ptA = next(p for p in parent.points if p['id'] == self.point_id_parent)
        ptB = next(p for p in child.points if p['id'] == self.point_id_child)
        # For now, just return a placeholder (real implementation would use poses)
        return [f"revolute({self.id})"]
    def __init__(self, id: str, name: str, parent: str, point_id_parent: str, child: str, point_id_child: str):
        super().__init__(id, name, "revolute", parent, child)
        self.point_id_parent = point_id_parent
        self.point_id_child = point_id_child

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "point_id_parent": self.point_id_parent,
            "point_id_child": self.point_id_child
        })
        return d

class PrismaticJoint(Joint):
    def constraint_equation(self, links_by_id, unit_angle):
        # Placeholder for prismatic joint constraint
        return [f"prismatic({self.id})"]
    def __init__(self, id: str, name: str, parent: str, axis_parent: dict, child: str, point_id_child: str = None, axis_child: dict = None, limits: Optional[dict] = None):
        super().__init__(id, name, "prismatic", parent, child)
        self.axis_parent = axis_parent
        self.point_id_child = point_id_child
        self.axis_child = axis_child
        self.limits = limits

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["axis_parent"] = self.axis_parent
        if self.point_id_child is not None:
            d["point_id_child"] = self.point_id_child
        if self.axis_child is not None:
            d["axis_child"] = self.axis_child
        if self.limits:
            d["limits"] = self.limits
        return d

class PinInSlotJoint(Joint):
    def constraint_equation(self, links_by_id, unit_angle):
        # Placeholder for pin-in-slot joint constraint
        return [f"pin-in-slot({self.id})"]
    def __init__(self, id: str, name: str, parent: str, line_id_parent: str, child: str, point_id_child: str):
        super().__init__(id, name, "pin-in-slot", parent, child)
        self.line_id_parent = line_id_parent
        self.point_id_child = point_id_child

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "line_id_parent": self.line_id_parent,
            "point_id_child": self.point_id_child
        })
        return d

class GearJoint(Joint):
    def constraint_equation(self, links_by_id, unit_angle):
        # Placeholder for gear joint constraint
        return [f"gear({self.id})"]
    def __init__(self, id: str, name: str, parent: str, child: str, ratio: float, phase_offset: float = 0.0):
        super().__init__(id, name, "gear", parent, child)
        self.ratio = ratio
        self.phase_offset = phase_offset

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "ratio": self.ratio,
            "phase_offset": self.phase_offset
        })
        return d

class WeldJoint(Joint):
    def constraint_equation(self, links_by_id, unit_angle):
        # Placeholder for weld joint constraint
        return [f"weld({self.id})"]
    def __init__(self, id: str, name: str, parent: str, child: str, relative_pose: dict):
        super().__init__(id, name, "weld", parent, child)
        self.relative_pose = relative_pose

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["relative_pose"] = self.relative_pose
        return d

class Linkage2D:

    def constraint_equations(self):
        """Assemble all joint constraint equations into a single list."""
        eqs = []
        links_by_id = {l.id: l for l in self.links}
        for joint in self.joints:
            eqs.extend(joint.constraint_equation(links_by_id, self.unit_angle))
        return eqs

    def solve_linkage(self, driven=None, initial_pose=None, verbose=2):
        """Numerically solve the linkage configuration using least squares."""
        # Prepare pose vector and indices for non-grounded links
        links = [l.to_dict() for l in self.links]
        joints = [j.to_dict() for j in self.joints]
        unit_angle = self.unit_angle
        # Identify non-grounded links
        pose_vec = []
        non_grounded_indices = []
        for i, link in enumerate(links):
            if not link.get('isGrounded', False):
                pose_vec.extend(link['pose']['position'] + [link['pose']['angle']])
                non_grounded_indices.append(i)
        pose_vec = np.array(pose_vec)
        if initial_pose is not None:
            pose_vec = np.array(initial_pose)

        def set_link_poses_from_vector(links, pose_vec, non_grounded_indices):
            idx = 0
            for i in non_grounded_indices:
                link = links[i]
                link['pose']['position'] = [float(pose_vec[idx]), float(pose_vec[idx+1])]
                link['pose']['angle'] = float(pose_vec[idx+2])
                idx += 3

        def fun(x):
            set_link_poses_from_vector(links, x, non_grounded_indices)
            # Use the procedural constraint_equations from solver.py for now
            from planar_linkage.solver import constraint_equations
            constraint_equations.unit_angle = unit_angle
            grounded_mask = [i not in non_grounded_indices for i in range(len(links))]
            return constraint_equations(x, links, joints, grounded_mask, driven=driven) if driven is not None else constraint_equations(x, links, joints, grounded_mask)

        x0 = pose_vec.copy()
        res = least_squares(fun, x0, verbose=verbose)
        set_link_poses_from_vector(links, res.x, non_grounded_indices)
        # Update self.links with solved poses
        for i, link in enumerate(self.links):
            link.pose = links[i]['pose']
        return res
    @classmethod
    def from_json(cls, data: dict):
        links = [Link2D(**link) for link in data.get('links', [])]
        joints = []
        for joint in data.get('joints', []):
            t = joint.get('type')
            if t == 'revolute':
                joints.append(RevoluteJoint(
                    id=joint['id'], name=joint['name'],
                    parent=joint['parent'], point_id_parent=joint['point_id_parent'],
                    child=joint['child'], point_id_child=joint['point_id_child']
                ))
            elif t == 'prismatic':
                joints.append(PrismaticJoint(
                    id=joint['id'], name=joint['name'],
                    parent=joint['parent'], axis_parent=joint['axis_parent'],
                    child=joint['child'],
                    point_id_child=joint.get('point_id_child'),
                    axis_child=joint.get('axis_child'),
                    limits=joint.get('limits')
                ))
            elif t == 'pin-in-slot':
                joints.append(PinInSlotJoint(
                    id=joint['id'], name=joint['name'],
                    parent=joint['parent'], line_id_parent=joint['line_id_parent'],
                    child=joint['child'], point_id_child=joint['point_id_child']
                ))
            elif t == 'gear':
                joints.append(GearJoint(
                    id=joint['id'], name=joint['name'],
                    parent=joint['parent'], child=joint['child'],
                    ratio=joint['ratio'], phase_offset=joint.get('phase_offset', 0.0)
                ))
            elif t == 'weld':
                joints.append(WeldJoint(
                    id=joint['id'], name=joint['name'],
                    parent=joint['parent'], child=joint['child'],
                    relative_pose=joint['relative_pose']
                ))
            else:
                raise ValueError(f"Unknown joint type: {t}")
        return cls(
            id=data['id'], name=data['name'], type=data['type'],
            unit_length=data['unit_length'], unit_angle=data['unit_angle'],
            convention=data['convention'], links=links, joints=joints,
            version=data.get('version', '1.0')
        )
    def __init__(self, id: str, name: str, type: str, unit_length: str, unit_angle: str, convention: dict,
                 links: List[Link2D], joints: List[Joint], version: str = "1.0"):
        self.id = id
        self.name = name
        self.type = type
        self.unit_length = unit_length
        self.unit_angle = unit_angle
        self.convention = convention
        self.links = links
        self.joints = joints
        self.version = version

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "unit_length": self.unit_length,
            "unit_angle": self.unit_angle,
            "convention": self.convention,
            "links": [l.to_dict() for l in self.links],
            "joints": [j.to_dict() for j in self.joints]
        }
