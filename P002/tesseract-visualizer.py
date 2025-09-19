"""
Tesseract visualizer (Pygame)

Save this file as `tesseract_visualizer.py` and run:
    python3 tesseract_visualizer.py

Requirements:
    pip install pygame numpy

What it does:
- Builds the 16 vertices and 32 edges of a 4D hypercube (tesseract).
- Lets you rotate the tesseract in 4D using several rotation planes.
- Projects 4D -> 3D (perspective) and then 3D -> 2D for display.
- Draws edges with simple depth-based brightness.

Controls:
  1..6    : select rotation plane (1=XY, 2=XZ, 3=XW, 4=YZ, 5=YW, 6=ZW)
  Arrow keys / QWERAS : rotate +/- in the active plane
  Mouse drag : rotate in XY and XZ for quick 3D feel
  SPACE    : toggle auto-rotation
  +/-      : change 4D-to-3D perspective distance
  R        : reset view
  C        : center/recapture mouse (no-op on most systems)
  ESC/Q    : quit

Notes:
- Units are arbitrary. Adjust `scale` and `proj_distance` to taste.
- This is intended as an educational and visual tool—feel free to modify.
"""

import pygame
import numpy as np
import sys
import math

# -------------------- Config --------------------
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (12, 12, 20)
EDGE_COLOR = (200, 200, 230)
FPS = 60

# Tesseract geometry: 16 vertices at all combinations of +/-1 in 4 coords
verts4 = np.array([[x, y, z, w]
                   for x in (-1, 1)
                   for y in (-1, 1)
                   for z in (-1, 1)
                   for w in (-1, 1)], dtype=float)

# Build edges: connect vertices that differ by exactly one coordinate
edges = []
for i in range(len(verts4)):
    for j in range(i+1, len(verts4)):
        if np.sum(np.abs(verts4[i] - verts4[j]) > 1e-6) == 1:
            edges.append((i, j))

# Rotation planes mapping
planes = [
    (0, 1),  # XY
    (0, 2),  # XZ
    (0, 3),  # XW
    (1, 2),  # YZ
    (1, 3),  # YW
    (2, 3),  # ZW
]
plane_names = ['XY', 'XZ', 'XW', 'YZ', 'YW', 'ZW']

# -------------------- Helpers --------------------

def rotation_matrix_4d(i, j, theta):
    """Create an identity 4x4 matrix, then add a rotation in plane (i,j)."""
    R = np.eye(4)
    c = math.cos(theta)
    s = math.sin(theta)
    R[i, i] = c
    R[j, j] = c
    R[i, j] = -s
    R[j, i] = s
    return R


def project_4d_to_3d(points4, dist=3.5):
    """Perspective project from 4D to 3D along the w axis.
    dist is distance of 3D "camera" from origin in w-direction.
    projection: for a 4D point (x,y,z,w) -> (x',y',z') = (x,y,z) / (d - w)
    """
    w = points4[:, 3]
    denom = (dist - w)
    # avoid division by zero
    denom = np.where(np.abs(denom) < 1e-6, 1e-6, denom)
    projected = points4[:, :3] / denom[:, np.newaxis]
    return projected


def project_3d_to_2d(points3, fov=400, viewer_z=4.0):
    """Project 3D -> 2D screen coords using simple perspective along z.
    fov scales the projection; viewer_z is how far the camera sits on z axis.
    """
    z = points3[:, 2] + viewer_z
    z = np.where(np.abs(z) < 1e-6, 1e-6, z)
    x2 = (points3[:, 0] * fov) / z
    y2 = (points3[:, 1] * fov) / z
    return np.vstack([x2, y2]).T


def transform_and_project(verts4, rot_matrix, proj_dist, fov, viewer_z, scale, center):
    # Rotate in 4D
    rotated4 = verts4.dot(rot_matrix.T)
    # 4D -> 3D
    p3 = project_4d_to_3d(rotated4, dist=proj_dist)
    # 3D rotations for nicer viewing (optional)
    # 3D -> 2D
    p2 = project_3d_to_2d(p3 * scale, fov=fov, viewer_z=viewer_z)
    # map to screen coords
    p2[:, 0] += center[0]
    p2[:, 1] += center[1]
    return p2, p3

# -------------------- Main App --------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tesseract Visualizer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Consolas', 16)

    # View params
    scale = 120.0
    proj_distance = 3.5
    fov = 450
    viewer_z = 3.0

    auto_rotate = True
    rot_speed = 0.8  # radians per second when auto-rotating

    # cumulative 4D rotation matrix (start identity)
    rot4 = np.eye(4)

    # active rotation plane index
    active_plane = 0

    # mouse drag state
    mouse_down = False
    last_mouse = None

    # precompute a small easing rotation to apply per-frame for auto-rotate
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    auto_rotate = not auto_rotate
                elif event.key == pygame.K_r:
                    rot4 = np.eye(4)
                    proj_distance = 3.5
                elif event.key == pygame.K_c:
                    pass
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    proj_distance += 0.2
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    proj_distance = max(0.6, proj_distance - 0.2)
                elif event.key == pygame.K_1:
                    active_plane = 0
                elif event.key == pygame.K_2:
                    active_plane = 1
                elif event.key == pygame.K_3:
                    active_plane = 2
                elif event.key == pygame.K_4:
                    active_plane = 3
                elif event.key == pygame.K_5:
                    active_plane = 4
                elif event.key == pygame.K_6:
                    active_plane = 5

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_mouse = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
                    last_mouse = None
            elif event.type == pygame.MOUSEMOTION and mouse_down:
                x, y = pygame.mouse.get_pos()
                lx, ly = last_mouse
                dx = (x - lx) * 0.01
                dy = (y - ly) * 0.01
                # quick 3D rotations (apply to rot4 but restricted to 3D subspace)
                Rxy = rotation_matrix_4d(0, 1, dx)
                Rxz = rotation_matrix_4d(0, 2, dy)
                rot4 = Rxy.dot(Rxz).dot(rot4)
                last_mouse = (x, y)

        # continuous input for keyboard-controlled rotations
        keys = pygame.key.get_pressed()
        # arrow keys / QWERAS mapping
        delta = 0.0
        if keys[pygame.K_LEFT]:
            delta = -1.6 * dt
        if keys[pygame.K_RIGHT]:
            delta = 1.6 * dt
        if keys[pygame.K_UP]:
            delta = -1.6 * dt
        if keys[pygame.K_DOWN]:
            delta = 1.6 * dt

        # alternative plane-specific controls: Q/W for +/-, E/R, A/S etc mapped to planes
        plane_key_map = [ (pygame.K_q, pygame.K_w),
                          (pygame.K_e, pygame.K_r),
                          (pygame.K_t, pygame.K_y),
                          (pygame.K_a, pygame.K_s),
                          (pygame.K_d, pygame.K_f),
                          (pygame.K_g, pygame.K_h) ]
        for i,(kneg,kpos) in enumerate(plane_key_map):
            if keys[kneg]:
                rot = rotation_matrix_4d(*planes[i], -1.8 * dt)
                rot4 = rot.dot(rot4)
            if keys[kpos]:
                rot = rotation_matrix_4d(*planes[i], 1.8 * dt)
                rot4 = rot.dot(rot4)

        # auto-rotate applies small rotations in a combination of planes for a pleasing effect
        if auto_rotate:
            # rotate slowly in multiple planes
            rot4 = rotation_matrix_4d(0,1, 0.25 * rot_speed * dt).dot(rot4)
            rot4 = rotation_matrix_4d(2,3, 0.15 * rot_speed * dt).dot(rot4)
            rot4 = rotation_matrix_4d(0,3, 0.18 * rot_speed * dt).dot(rot4)

        # transform and project vertices
        center = (WIDTH//2, HEIGHT//2)
        points2d, points3d = transform_and_project(verts4, rot4, proj_distance, fov, viewer_z, scale, center)

        # draw
        screen.fill(BG_COLOR)

        # draw edges with depth cueing
        # compute depth as avg z (after 4D->3D projection)
        depths = []
        for (i,j) in edges:
            z_avg = (points3d[i,2] + points3d[j,2]) / 2.0
            depths.append((z_avg, i, j))
        # sort by depth (far to near)
        depths.sort()
        for z_avg, i, j in depths:
            p1 = points2d[i]
            p2 = points2d[j]
            # depth shading: nearer edges brighter
            shade = int(120 + 120 * (1.0 / (1.0 + math.exp(- (z_avg + 0.5)))) )
            color = (min(255, shade+60), min(255, shade+60), min(255, shade+80))
            pygame.draw.aaline(screen, color, p1, p2, 1)

        # draw vertices as circles (optional)
        for idx, p in enumerate(points2d):
            z = points3d[idx,2]
            r = int(max(2, 6 * (1.0 / (0.8 + z))))
            shade = int(120 + 120 * (1.0 / (1.0 + math.exp(- (z + 0.5)))) )
            col = (shade+50, shade+50, 255)
            pygame.draw.circle(screen, col, (int(p[0]), int(p[1])), r)

        # HUD
        hud_y = 10
        lines = [
            f"Plane: {plane_names[active_plane]}   (1-6 switch)",
            "Q/W E/R T/Y  A/S D/F  G/H : rotate specific planes",
            f"Auto-rotate: {'ON' if auto_rotate else 'OFF'}   (SPACE to toggle)",
            f"4D->3D distance: {proj_distance:.2f}   (+/- to change)",
            "Mouse-drag: rotate in 3D",
            "R: reset    ESC/Q: quit"
        ]
        for line in lines:
            surf = font.render(line, True, (220,220,220))
            screen.blit(surf, (10, hud_y))
            hud_y += 20

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
