"""Separate male-to-female 90-degree elbow for the measured DeWalt REV 5 adapter.

Native axes: male tip at X=0, airflow initially +X, female outlet toward -Z.
The installed elbow may extend below the card. Fit and support removal need
physical testing; this is not a claim of support-free printing. All mm.
"""
import argparse
from math import asin, atan2, cos, degrees, hypot, pi, sin
from pathlib import Path

from build123d import Align, Circle, Cone, Cylinder, Pos, Rot, export_step, export_stl, loft
from dewalt_rev5_adapter import build_dewalt_adapter, socket_dimensions


def connection_dimensions(kind):
    """Female socket geometry already used by the corresponding card adapter."""
    if kind == 'dewalt':
        return socket_dimensions()
    if kind == 'stanley':
        return dict(connector_od=30.75, clearance=.4, taper=2., depth=35.)
    raise ValueError(f'Unknown connection: {kind}')


def build_addon_elbow(bend_radius=32.0, male_diameter_adjustment=0.0,
                      inlet='dewalt', outlet='dewalt'):
    socket = connection_dimensions(outlet)
    upstream = connection_dimensions(inlet)
    depth, wall, neck, lead_in = socket['depth'], 3.0, 5.0, 1.5
    female_root = (socket['connector_od']+socket['clearance']-socket['taper']/2)/2
    female_mouth = female_root+socket['taper']/2
    # Male follows the existing female socket taper with 0.20 mm diametral
    # clearance. For DeWalt this reproduces the measured cuff. Stanley's
    # female fit was tested; this complementary printed male is still new.
    male_tip = (upstream['connector_od']+upstream['clearance']
                -upstream['taper']/2-.2+male_diameter_adjustment)/2
    male_base = male_tip+upstream['taper']/2
    bore_tip, bore_base = male_tip-wall, male_base-wall
    upstream_outer = (upstream['connector_od']+upstream['clearance']+upstream['taper']/2)/2+wall
    shoulder_radius = upstream_outer+.5
    if not -1 <= male_diameter_adjustment <= 1 or bore_tip <= 0:
        raise ValueError('Male diameter adjustment must be between -1 and +1 mm')
    if bend_radius <= max(male_base, female_root+wall):
        raise ValueError('Bend radius must exceed the largest outside duct radius')
    alignment = (Align.CENTER, Align.CENTER, Align.MIN)
    male_axis = Rot(0, 90, 0)
    outer = male_axis*Cone(male_tip, male_base, depth, align=alignment)
    slope = (bore_base-bore_tip)/depth
    inner = Pos(-.1, 0, 0)*male_axis*Cone(
        bore_tip-.1*slope, bore_base, depth+.1, align=alignment)
    # A positive shoulder stops the plug at the socket mouth. Neck provides
    # clearance between the original supported body and the new downward bend.
    outer += Pos(depth, 0, 0)*male_axis*Cone(
        shoulder_radius, male_base, neck, align=alignment)
    inner += Pos(depth, 0, 0)*male_axis*Cylinder(bore_base, neck, align=alignment)
    sections = []
    for i in range(17):
        t = i/16
        a = pi*t/2
        radius = bore_base+(female_root-bore_base)*(3*t*t-2*t*t*t)
        loc = Pos(depth+neck+bend_radius*sin(a), 0,
                  -bend_radius*(1-cos(a)))*Rot(0, 90+degrees(a), 0)
        sections.append((loc, radius))
    outer += loft([loc*Circle(r+wall) for loc, r in sections])
    inner += loft([loc*Circle(r) for loc, r in sections])
    female_axis = Pos(depth+neck+bend_radius, 0, -bend_radius)*Rot(0, 180, 0)
    outer += female_axis*Cylinder(female_mouth+wall, depth, align=alignment)
    inner += female_axis*Cone(female_root, female_mouth+.1*(female_mouth-female_root)/depth,
                              depth+.1, align=alignment)
    inner += female_axis*Pos(0, 0, depth-lead_in)*Cone(
        female_mouth-(female_mouth-female_root)*lead_in/depth,
        female_mouth+1, lead_in+.01, align=alignment)
    part = outer-inner
    if not part.is_valid or len(part.solids()) != 1:
        raise RuntimeError('Expected one valid elbow solid')
    part.label = f'90 degree elbow — {inlet} male to {outlet} female'
    return part, dict(inlet=inlet, outlet=outlet,
                      male_tip_od=male_tip*2, male_base_od=male_base*2,
                      male_engagement=depth, minimum_bore=bore_tip*2,
                      female_root_id=female_root*2, female_mouth_id=female_mouth*2,
                      female_engagement=depth, bend_radius=bend_radius,
                      socket_outer_radius=female_mouth+wall,
                      upstream_socket_outer_radius=upstream_outer)


def installed_location(socket_outer_radius, inlet='dewalt'):
    # Match hose_socket_concept's automatic aim for the measured REV 5 model:
    # 32 mm first bend + 6 mm neck + 35 mm socket, limited to X=32 mm.
    initial_radius = 32 if inlet == 'dewalt' else 24
    length = initial_radius+6+35
    half_width = max(19.5, socket_outer_radius)
    angle = -90+min(30, max(0, degrees(asin(32/hypot(length, half_width))
                                      -atan2(half_width, length))))
    return Rot(0, 0, angle)*Pos(initial_radius+6, 0, 3.4+initial_radius)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bend-radius', type=float, default=32)
    parser.add_argument('--male-diameter-adjustment', type=float, default=0)
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()
    part, dimensions = build_addon_elbow(args.bend_radius, args.male_diameter_adjustment)
    output = Path(__file__).resolve().parents[1]/'exports'
    output.mkdir(parents=True, exist_ok=True)
    # Standalone export sits on its female socket rim. Its final print
    # orientation/support strategy still needs checking in the slicer.
    printable = Pos(0, 0, -part.bounding_box().min.Z)*part
    for ext, exporter in [('step', export_step), ('stl', export_stl)]:
        path = output/f'dewalt-addon-90-elbow.{ext}'
        if not exporter(printable, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    print(f'Valid single solid; volume {part.volume:.1f} mm³; dimensions: {dimensions}')
    if args.show:
        from ocp_viewer import Camera, show
        existing = build_dewalt_adapter()
        installed = installed_location(dimensions['socket_outer_radius'])*part
        interference = existing.intersect(installed)
        collision_volume = interference.volume if interference else 0
        print(f'Installed interference volume: {collision_volume:.6f} mm³')
        if collision_volume > .01:
            raise RuntimeError('Add-on elbow collides with the existing adapter')
        show(existing, installed, Pos(140, 0, 0)*printable,
             names=['Existing REV 5 DeWalt card adapter',
                    'NEW plug-in 90 elbow — outlet -Z', 'Same elbow separately — print preview'],
             colors=['#c7cdd3', '#e8a242', '#e8a242'],
             reset_camera=Camera.RESET, axes=False, axes0=True, grid=False,
             position=(260, -290, 180), target=(55, -30, 25), up='Z', port=3939)


if __name__ == '__main__':
    main()
