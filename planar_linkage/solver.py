import json
import numpy as np
from scipy.optimize import least_squares
import math

def transform_point(local_pos, pose, unit_angle='deg'):
    x, y = local_pos
    angle = pose.get('angle', 0)
    if unit_angle == 'deg':
        angle = math.radians(angle)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    tx, ty = pose.get('position', [0, 0])
    wx = cos_a * x - sin_a * y + tx
    wy = sin_a * x + cos_a * y + ty
    return [wx, wy]

def get_link_pose_vector(links):
    pose_vec = []
    non_grounded_indices = []
    for i, link in enumerate(links):
        if not link.get('isGrounded', False):
            pose_vec.extend(link['pose']['position'] + [link['pose']['angle']])
            non_grounded_indices.append(i)
    return np.array(pose_vec), non_grounded_indices

def set_link_poses_from_vector(links, pose_vec, non_grounded_indices):
    idx = 0
    for i in non_grounded_indices:
        link = links[i]
        link['pose']['position'] = [float(pose_vec[idx]), float(pose_vec[idx+1])]
        link['pose']['angle'] = float(pose_vec[idx+2])
        idx += 3


def constraint_equations(pose_vec, links, joints, grounded_mask, driven=None):
    set_link_poses_from_vector(links, pose_vec, [i for i, g in enumerate(grounded_mask) if not g])
    eqs = []
    unit_angle = constraint_equations.unit_angle if hasattr(constraint_equations, 'unit_angle') else 'deg'
    for joint in joints:
        if joint['type'] == 'revolute':
            parent_id = joint['parent']
            child_id = joint['child']
            parent_pt_id = joint['point_id_parent']
            child_pt_id = joint['point_id_child']
            parent_link = next(l for l in links if l['id'] == parent_id)
            child_link = next(l for l in links if l['id'] == child_id)
            parent_pt = next(p for p in parent_link['points'] if p['id'] == parent_pt_id)
            child_pt = next(p for p in child_link['points'] if p['id'] == child_pt_id)
            parent_global = transform_point(parent_pt['position'], parent_link['pose'], unit_angle)
            child_global = transform_point(child_pt['position'], child_link['pose'], unit_angle)
            eqs.extend([parent_global[0] - child_global[0], parent_global[1] - child_global[1]])
        elif joint['type'] == 'prismatic':
            parent_id = joint['parent']
            child_id = joint['child']
            axis_parent = joint['axis_parent']
            axis_child = joint['axis_child']
            axis_point_id_p = axis_parent['point_id']
            axis_dir_id_p = axis_parent['direction_id']
            axis_point_id_c = axis_child['point_id']
            axis_dir_id_c = axis_child['direction_id']
            parent_link = next(l for l in links if l['id'] == parent_id)
            child_link = next(l for l in links if l['id'] == child_id)
            axis_point_p = next(p for p in parent_link['points'] if p['id'] == axis_point_id_p)
            axis_dir_p = next(d for d in parent_link.get('directions', []) if d['id'] == axis_dir_id_p)
            axis_point_c = next(p for p in child_link['points'] if p['id'] == axis_point_id_c)
            axis_dir_c = next(d for d in child_link.get('directions', []) if d['id'] == axis_dir_id_c)
            # Get local direction angles
            axis_angle_p = axis_dir_p.get('angle', 0)
            axis_angle_c = axis_dir_c.get('angle', 0)
            # Add link pose angle to local direction angle to get world direction angle
            parent_pose_angle = parent_link['pose'].get('angle', 0)
            child_pose_angle = child_link['pose'].get('angle', 0)
            if unit_angle == 'deg':
                axis_angle_p = math.radians(axis_angle_p)
                axis_angle_c = math.radians(axis_angle_c)
                parent_pose_angle = math.radians(parent_pose_angle)
                child_pose_angle = math.radians(child_pose_angle)
            world_axis_angle_p = axis_angle_p + parent_pose_angle
            world_axis_angle_c = axis_angle_c + child_pose_angle
            dir_vec_p = np.array([math.cos(world_axis_angle_p), math.sin(world_axis_angle_p)])
            dir_vec_c = np.array([math.cos(world_axis_angle_c), math.sin(world_axis_angle_c)])
            axis_origin_p = transform_point(axis_point_p['position'], parent_link['pose'], unit_angle)
            axis_origin_c = transform_point(axis_point_c['position'], child_link['pose'], unit_angle)
            v = np.array(axis_origin_c) - np.array(axis_origin_p)
            # Constraint 1: directions must be parallel (cross product = 0)
            eqs.append(dir_vec_p[0]*dir_vec_c[1] - dir_vec_p[1]*dir_vec_c[0])
            # Constraint 2: axis origins must be colinear along axis direction (cross product = 0)
            eqs.append(v[0]*dir_vec_p[1] - v[1]*dir_vec_p[0])
        elif joint['type'] == 'pin-in-slot':
            parent_id = joint['parent']
            child_id = joint['child']
            line_id = joint['line_id_parent']
            point_id = joint['point_id_child']
            parent_link = next(l for l in links if l['id'] == parent_id)
            child_link = next(l for l in links if l['id'] == child_id)
            # Find the line object on the parent link
            line = next(ln for ln in parent_link['lines'] if ln['id'] == line_id)
            ptA_id, ptB_id = line['point_ids']
            ptA = next(p for p in parent_link['points'] if p['id'] == ptA_id)
            ptB = next(p for p in parent_link['points'] if p['id'] == ptB_id)
            A = np.array(transform_point(ptA['position'], parent_link['pose'], unit_angle))
            B = np.array(transform_point(ptB['position'], parent_link['pose'], unit_angle))
            pin = next(p for p in child_link['points'] if p['id'] == point_id)
            P = np.array(transform_point(pin['position'], child_link['pose'], unit_angle))
            # Constraint: P must be on line AB (cross product = 0)
            AB = B - A
            AP = P - A
            cross = AB[0]*AP[1] - AB[1]*AP[0]
            eqs.append(cross)
        elif joint['type'] == 'weld':
            parent_id = joint['parent']
            child_id = joint['child']
            rel_pos = joint.get('relative_pos', [0, 0])
            rel_angle = joint.get('relative_angle', 0)
            parent_link = next(l for l in links if l['id'] == parent_id)
            child_link = next(l for l in links if l['id'] == child_id)
            # Transform the relative position from parent to world
            parent_pose = parent_link['pose']
            child_pose = child_link['pose']
            # Compute world position of the weld point on parent
            weld_world = transform_point(rel_pos, parent_pose, unit_angle)
            # The origin of the child link in world coordinates
            child_origin = transform_point([0, 0], child_pose, unit_angle)
            # Constraint 1 & 2: positions must coincide
            eqs.extend([weld_world[0] - child_origin[0], weld_world[1] - child_origin[1]])
            # Constraint 3: angles must differ by rel_angle
            parent_angle = parent_pose.get('angle', 0)
            child_angle = child_pose.get('angle', 0)
            if unit_angle == 'deg':
                eqs.append((child_angle - parent_angle) - rel_angle)
            else:
                eqs.append((child_angle - parent_angle) - rel_angle)
        else:
            pass
    # Add driven constraint if specified (for animation)
    if driven is not None:
        child_id, parent_id, target_rel_angle = driven
        parent_link = next(l for l in links if l['id'] == parent_id)
        child_link = next(l for l in links if l['id'] == child_id)
        parent_angle = parent_link['pose']['angle']
        child_angle = child_link['pose']['angle']
        if unit_angle == 'deg':
            eqs.append((child_angle - parent_angle) - target_rel_angle)
        else:
            eqs.append((child_angle - parent_angle) - target_rel_angle)
    return np.array(eqs)

def solve_linkage(json_file_or_data, driven=None, initial_pose=None):
    # Accept either a filename or a data dict
    if isinstance(json_file_or_data, str):
        with open(json_file_or_data, 'r', encoding='utf-8') as f:
            data = json.load(f)
        json_file = json_file_or_data
    else:
        data = json_file_or_data
        json_file = None
    links = data['links']
    joints = data['joints']
    unit_angle = data.get('unit_angle', 'deg')
    pose_vec, non_grounded_indices = get_link_pose_vector(links)
    if initial_pose is not None:
        pose_vec = initial_pose.copy()
    def fun(x):
        set_link_poses_from_vector(links, x, non_grounded_indices)
        constraint_equations.unit_angle = unit_angle
        return constraint_equations(x, links, joints, [i not in non_grounded_indices for i in range(len(links))], driven=driven) if driven is not None else constraint_equations(x, links, joints, [i not in non_grounded_indices for i in range(len(links))])
    x0 = pose_vec.copy()
    res = least_squares(fun, x0, verbose=2)
    set_link_poses_from_vector(links, res.x, non_grounded_indices)
    data['links'] = links
    if json_file:
        with open('solved_'+json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f'Solved linkage saved to solved_{json_file}')
        return data
    else:
        return data, res.x
