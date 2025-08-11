import argparse
import json
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from planar_linkage import solve_linkage, transform_point
from jsonschema import validate, Draft202012Validator
from jsonschema.exceptions import ValidationError
import matplotlib.animation as animation
import numpy as np
from copy import deepcopy
from planar_linkage.linkage2d import Linkage2D

def validate_json(schema_path, data_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=schema, cls=Draft202012Validator)
        print(f"VALID: {data_path} conforms to {schema_path}")
        return 0
    except ValidationError as e:
        print("INVALID JSON linkage.")
        print(f"Message : {e.message}")
        print(f"Path    : {'/'.join([str(p) for p in e.path])}")
        print(f"Schema  : {'/'.join([str(p) for p in e.schema_path])}")
        return 1

def plot_linkage(data, ax=None):
    unit_angle = data.get('unit_angle', 'deg')
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    link_points = {}
    for link in data['links']:
        pose = link.get('pose', {'position': [0, 0], 'angle': 0})
        pts = {}
        origin = transform_point([0, 0], pose, unit_angle)
        axis_len = 40
        x_axis_end = transform_point([axis_len, 0], pose, unit_angle)
        y_axis_end = transform_point([0, axis_len], pose, unit_angle)
        ax.arrow(origin[0], origin[1], x_axis_end[0]-origin[0], x_axis_end[1]-origin[1], head_width=8, head_length=12, fc='r', ec='r')
        ax.arrow(origin[0], origin[1], y_axis_end[0]-origin[0], y_axis_end[1]-origin[1], head_width=8, head_length=12, fc='g', ec='g')
        ax.text(origin[0], origin[1], link['id'], fontsize=10, color='purple', ha='left', va='top')
        for pt in link.get('points', []):
            world_pt = transform_point(pt['position'], pose, unit_angle)
            pts[pt['id']] = world_pt
            ax.plot(world_pt[0], world_pt[1], 'o', color='red', markersize=6)
            ax.text(world_pt[0], world_pt[1], pt['id'], fontsize=9, ha='right', va='bottom')
        pt_ids = list(pts.keys())
        for i in range(len(pt_ids)):
            for j in range(i+1, len(pt_ids)):
                p1 = pts[pt_ids[i]]
                p2 = pts[pt_ids[j]]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], '-', color='black', linewidth=3)
        link_points[link['id']] = pts

        # Draw circles
        for circle in link.get('circles', []):
            center_id = circle['center_point_id']
            radius = circle['radius']
            if center_id in pts:
                center = pts[center_id]
            else:
                # Fallback: transform center point if not in pts
                center_pt = next((p for p in link.get('points', []) if p['id'] == center_id), None)
                if center_pt is not None:
                    center = transform_point(center_pt['position'], pose, unit_angle)
                else:
                    continue
            circ_patch = mpatches.Circle(center, radius, fill=False, color='blue', linewidth=2, linestyle='--')
            ax.add_patch(circ_patch)
    ax.set_title(data.get('name', 'Linkage'))
    ax.set_xlabel(f"X ({data.get('unit_length', 'mm')})")
    ax.set_ylabel(f"Y ({data.get('unit_length', 'mm')})")
    if ax is None:
        plt.show()

# OOP-based plotting for Linkage2D
def plot_linkage2d(linkage: Linkage2D, ax=None):
    unit_angle = linkage.unit_angle
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    for link in linkage.links:
        pose = link.pose
        origin = transform_point([0, 0], pose, unit_angle)
        axis_len = 40
        x_axis_end = transform_point([axis_len, 0], pose, unit_angle)
        y_axis_end = transform_point([0, axis_len], pose, unit_angle)
        ax.arrow(origin[0], origin[1], x_axis_end[0]-origin[0], x_axis_end[1]-origin[1], head_width=8, head_length=12, fc='r', ec='r')
        ax.arrow(origin[0], origin[1], y_axis_end[0]-origin[0], y_axis_end[1]-origin[1], head_width=8, head_length=12, fc='g', ec='g')
        ax.text(origin[0], origin[1], link.id, fontsize=10, color='purple', ha='left', va='top')
        for pt in link.points:
            world_pt = transform_point(pt['position'], pose, unit_angle)
            ax.plot(world_pt[0], world_pt[1], 'o', color='red', markersize=6)
            ax.text(world_pt[0], world_pt[1], pt['id'], fontsize=9, ha='right', va='bottom')
        pt_ids = [pt['id'] for pt in link.points]
        pts = {pt['id']: transform_point(pt['position'], pose, unit_angle) for pt in link.points}
        for i in range(len(pt_ids)):
            for j in range(i+1, len(pt_ids)):
                p1 = pts[pt_ids[i]]
                p2 = pts[pt_ids[j]]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], '-', color='black', linewidth=3)
        for circle in link.circles:
            center_id = circle.get('center_point_id')
            radius = circle['radius']
            if center_id and center_id in pts:
                center = pts[center_id]
            else:
                center = None
                if 'center' in circle:
                    center = transform_point(circle['center'], pose, unit_angle)
                elif 'center_id' in circle:
                    for pt in link.points:
                        if pt['id'] == circle['center_id']:
                            center = transform_point(pt['position'], pose, unit_angle)
                            break
            if center is not None:
                circ_patch = mpatches.Circle(center, radius, fill=False, color='blue', linewidth=2, linestyle='--')
                ax.add_patch(circ_patch)
    ax.set_title(linkage.name)
    ax.set_xlabel(f"X ({linkage.unit_length})")
    ax.set_ylabel(f"Y ({linkage.unit_length})")
    if ax is None:
        plt.show()

# OOP-based animation for Linkage2D
def animate_linkage2d(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    linkage = Linkage2D.from_json(data)
    # Find the first revolute joint as the crank (or 'R1' if present)
    crank_joint = None
    for joint in linkage.joints:
        if getattr(joint, 'type', None) == 'revolute' and (joint.id == 'R1' or crank_joint is None):
            crank_joint = joint
            if joint.id == 'R1':
                break
    if crank_joint is None:
        raise ValueError("No revolute joint found to drive as crank.")
    parent_id = crank_joint.parent
    child_id = crank_joint.child
    parent_link = next(l for l in linkage.links if l.id == parent_id)
    parent_angle = parent_link.pose['angle']
    unit_angle = linkage.unit_angle
    fig, ax = plt.subplots(figsize=(8, 6))
    n_frames = 90
    angles = np.linspace(0, 360 if unit_angle=='deg' else 2*np.pi, n_frames)

    # Compute bounding box for all points in all frames (using initial pose)
    all_points = []
    temp_linkage = Linkage2D.from_json(data)
    for drive_angle in angles:
        driven = (child_id, parent_id, drive_angle)
        temp_linkage.solve_linkage(driven=driven, initial_pose=None, verbose=0)
        for link in temp_linkage.links:
            pose = link.pose
            for pt in link.points:
                world_pt = transform_point(pt['position'], pose, unit_angle)
                all_points.append(world_pt)
    all_points = np.array(all_points)
    x_min, y_min = np.min(all_points, axis=0)
    x_max, y_max = np.max(all_points, axis=0)
    pad = 20
    xlim = (x_min - pad, x_max + pad)
    ylim = (y_min - pad, y_max + pad)

    # Prepare pose vector for continuity
    pose_guess = None

    def animate_frame(i):
        nonlocal pose_guess
        ax.clear()
        drive_angle = angles[i]
        driven = (child_id, parent_id, drive_angle)
        # Use the same linkage object, only update poses
        linkage.solve_linkage(driven=driven, initial_pose=pose_guess, verbose=0)
        # Extract pose vector for next frame
        pose_guess = []
        for link in linkage.links:
            if not link.isGrounded:
                pose_guess.extend(link.pose['position'])
                pose_guess.append(link.pose['angle'])
        plot_linkage2d(linkage, ax=ax)
        ax.set_title(f"{linkage.name}\n{crank_joint.id} angle: {drive_angle:.1f} {unit_angle}")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    ani = animation.FuncAnimation(fig, animate_frame, frames=n_frames, interval=50, repeat=True)
    plt.show()

def solve_and_plot(json_file):
    solve_linkage(json_file)
    with open('solved_' + json_file, 'r', encoding='utf-8') as f:
        solved_data = json.load(f)
    plot_linkage(solved_data)
    plt.show()

def visualize(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    plot_linkage(data)
    plt.show()

def animate(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    joints = data['joints']
    r1 = next(j for j in joints if j['id'] == 'R1')
    parent_id = r1['parent']
    child_id = r1['child']
    parent_link = next(l for l in data['links'] if l['id'] == parent_id)
    parent_angle = parent_link['pose']['angle']
    unit_angle = data.get('unit_angle', 'deg')
    fig, ax = plt.subplots(figsize=(8, 6))
    n_frames = 90
    angles = np.linspace(0, 360 if unit_angle=='deg' else 2*np.pi, n_frames)
    pose_guess = [None]

    # Compute bounding box for all points in all frames
    all_points = []
    for drive_angle in angles:
        driven = (child_id, parent_id, drive_angle)
        data_frame = deepcopy(data)
        from planar_linkage import solve_linkage as solve_linkage_anim
        solved, _ = solve_linkage_anim(data_frame, driven=driven, initial_pose=None)
        for link in solved['links']:
            pose = link.get('pose', {'position': [0, 0], 'angle': 0})
            for pt in link.get('points', []):
                world_pt = transform_point(pt['position'], pose, unit_angle)
                all_points.append(world_pt)
    all_points = np.array(all_points)
    x_min, y_min = np.min(all_points, axis=0)
    x_max, y_max = np.max(all_points, axis=0)
    pad = 20
    xlim = (x_min - pad, x_max + pad)
    ylim = (y_min - pad, y_max + pad)

    def animate_frame(i):
        ax.clear()
        drive_angle = angles[i]
        driven = (child_id, parent_id, drive_angle)
        data_frame = deepcopy(data)
        from planar_linkage import solve_linkage as solve_linkage_anim
        solved, pose = solve_linkage_anim(data_frame, driven=driven, initial_pose=pose_guess[0])
        pose_guess[0] = pose
        plot_linkage(solved, ax=ax)
        ax.set_title(f"{data.get('name', 'Linkage')}\nR1 angle: {drive_angle:.1f} {unit_angle}")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    ani = animation.FuncAnimation(fig, animate_frame, frames=n_frames, interval=50, repeat=True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Planar Linkage Tools")
    parser.epilog = (
        "\nTest examples (from project root):\n"
        "  python linkage_tools.py validate planar_linkage.schema.json four_bar.json\n"
        "  python linkage_tools.py validate planar_linkage.schema.json crank_slider.json\n"
        "  python linkage_tools.py visualize four_bar.json\n"
        "  python linkage_tools.py visualize crank_slider.json\n"
        "  python linkage_tools.py solve_and_plot four_bar.json\n"
        "  python linkage_tools.py solve_and_plot crank_slider.json\n"
        "  python linkage_tools.py animate four_bar.json\n"
        "  python linkage_tools.py animate crank_slider.json\n"
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_validate = subparsers.add_parser('validate', help='Validate a linkage JSON against a schema')
    parser_validate.add_argument('schema', help='Path to schema file')
    parser_validate.add_argument('json', help='Path to linkage JSON file')

    parser_visualize = subparsers.add_parser('visualize', help='Visualize a linkage JSON')
    parser_visualize.add_argument('json', help='Path to linkage JSON file')

    parser_solve = subparsers.add_parser('solve_and_plot', help='Solve and plot a linkage')
    parser_solve.add_argument('json', help='Path to linkage JSON file')

    parser_animate = subparsers.add_parser('animate', help='Animate a linkage by driving R1')
    parser_animate.add_argument('json', help='Path to linkage JSON file')

    parser_animate2d = subparsers.add_parser('animate2d', help='Animate a linkage (OOP Linkage2D) by driving the crank')
    parser_animate2d.add_argument('json', help='Path to linkage JSON file')

    args = parser.parse_args()
    if args.command == 'validate':
        sys.exit(validate_json(args.schema, args.json))
    elif args.command == 'visualize':
        visualize(args.json)
    elif args.command == 'solve_and_plot':
        solve_and_plot(args.json)
    elif args.command == 'animate':
        animate(args.json)
    elif args.command == 'animate2d':
        animate_linkage2d(args.json)

if __name__ == "__main__":
    # Example usage:
    # python linkage_tools.py validate planar_linkage.schema.json four_bar.json
    # python linkage_tools.py validate planar_linkage.schema.json crank_slider.json
    # python linkage_tools.py visualize four_bar.json
    # python linkage_tools.py visualize crank_slider.json
    # python linkage_tools.py solve_and_plot four_bar.json
    # python linkage_tools.py solve_and_plot crank_slider.json
    # python linkage_tools.py animate four_bar.json
    # python linkage_tools.py animate crank_slider.json
    main()
