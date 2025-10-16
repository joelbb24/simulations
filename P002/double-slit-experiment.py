"""
double_slit.py

Double-slit demo in Pygame.

Controls:
  W        : toggle wave (continuous intensity) view on/off
  P        : toggle particle build-up view on/off
  SPACE    : emit a burst of particles (or hold to emit continuously)
  C        : clear particle hits
  UP/DOWN  : increase / decrease wavelength (visual effect)
  LEFT/RIGHT : increase / decrease slit separation
  S        : toggle single-slit envelope (on/off)
  ESC/Q    : quit

Notes:
- The program computes the intensity on the screen by summing complex
  contributions from two point-like coherent sources (slits) and taking |E|^2.
- Particles land on the screen probabilistically according to intensity.
- For simplicity: units are arbitrary; everything is normalized for display.
"""

import pygame
import numpy as np
import sys
import math
import random
from pygame import gfxdraw

# -------- Parameters ----------
SCREEN_W = 1080
SCREEN_H = 900
FPS = 60

# Physical-ish parameters (all in same arbitrary length units)
L = 400.0           # distance from slits to screen (x distance)
slit_center_x = 100 # x of slits (for drawing only)
slit_y_center = SCREEN_H / 2.0
slit_separation = 30.0   # separation between slit centers (adjustable)
wavelength = 20.0        # wavelength (affects fringe spacing) - adjustable
k = 2.0 * math.pi / wavelength

# Intensity precomputation resolution (one per pixel row)
rows = SCREEN_H
screen_x = SCREEN_W - (slit_center_x + 50)  # usable screen x-offset for display

# Detector (screen) x coordinate relative to slit positions
screen_x_pos = L

# Particle emission params
particles_per_second = 120
particles_batch = 200

# Visual scaling
intensity_scale = 1.0

# Envelope (single-slit) toggle
use_envelope = True

# -------- Pygame init ----------
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Double-slit simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 16)

# Precompute vertical positions of detector on "screen plane"
# We'll assume slits at x=0 in physics coordinates; map to Pygame display later
ys = np.linspace(0, SCREEN_H - 1, rows)

# Particles accumulation (list of y positions)
particle_hits = []  # list of integers (row indices)
particle_counts = np.zeros(rows, dtype=np.int32)

# Mode flags
show_wave = True
show_particles = True
emit = False

# Helper: compute intensity distribution given parameters
def compute_intensity(slit_sep, lam, L_dist, rows_array, use_envelope_flag=True):
    """
    slit_sep: distance between slits (center-to-center)
    lam: wavelength
    L_dist: screen distance from slits
    rows_array: array of y positions (pixels)
    returns: normalized intensity array (length rows_array)
    """
    # positions of slits in (x,y) coords; set slits at x=0, y = +/- slit_sep/2
    slit1 = np.array([0.0, -slit_sep / 2.0])
    slit2 = np.array([0.0, +slit_sep / 2.0])

    # screen points at x = L_dist, y = rows_array - center offset
    # translate pixel coordinates into the same units as slit separation:
    # We'll set 1 pixel == 1 length unit (arbitrary)
    y_phys = rows_array - (SCREEN_H / 2.0)
    x_phys = L_dist

    # compute distances r1,r2
    r1 = np.sqrt((x_phys - slit1[0])**2 + (y_phys - slit1[1])**2)
    r2 = np.sqrt((x_phys - slit2[0])**2 + (y_phys - slit2[1])**2)

    # complex field contributions (point-sources): E = A * exp(i k r) / r
    k_const = 2.0 * np.pi / lam
    # avoid division by zero
    r1 = np.maximum(r1, 1e-6)
    r2 = np.maximum(r2, 1e-6)

    # complex fields
    E1 = (1.0 / r1) * np.exp(1j * k_const * r1)
    E2 = (1.0 / r2) * np.exp(1j * k_const * r2)

    E = E1 + E2
    I = np.abs(E)**2  # intensity

    # Optionally apply single-slit envelope (approximate)
    if use_envelope_flag:
        # simple envelope: sinc-like pattern from finite slit width
        # approximate slit width w proportional to wavelength for visual interest
        slit_width = max(2.0, lam * 0.6)
        # angle approx: theta = y / L_dist
        theta = np.arctan2(y_phys, x_phys)
        beta = (np.pi * slit_width / lam) * np.sin(theta)
        envelope = np.ones_like(beta)
        # avoid division by zero for sinc
        near = np.abs(beta) < 1e-6
        envelope[~near] = (np.sin(beta[~near]) / beta[~near])**2
        envelope[near] = 1.0
        I *= envelope

    # normalize to max 1
    I /= np.max(I) + 1e-12
    return I

# Initial intensity
intensity = compute_intensity(slit_separation, wavelength, screen_x_pos, ys, use_envelope)

# Precompute cumulative distribution for sampling particles (update when intensity changes)
def make_cdf(intensity_array):
    probs = intensity_array + 1e-12
    probs = probs / probs.sum()
    cdf = np.cumsum(probs)
    return cdf

cdf = make_cdf(intensity)

# Particle emitter: sample y index from cdf
def sample_hit(cdf_array):
    r = random.random()
    # binary search
    idx = np.searchsorted(cdf_array, r)
    idx = min(max(0, idx), len(cdf_array)-1)
    return int(idx)

# Utility: render vertical intensity gradient
def draw_intensity_background(surface, intensity_array):
    # intensity_array length = rows
    # draw as vertical gradient on right portion of screen
    screen_draw_x = slit_center_x + 120  # left start of detector visualization
    detector_width = SCREEN_W - screen_draw_x - 20
    for i, val in enumerate(intensity_array):
        # map intensity to brightness 0..255
        b = int(255 * np.clip(val * intensity_scale, 0.0, 1.0))
        # use a color map: bluish -> yellowish when brighter
        col = (b, b, b)
        surface.fill(col, rect=(screen_draw_x, i, detector_width, 1))

# Text helper
def draw_text(surf, text, x, y, color=(255,255,255)):
    surf.blit(font.render(text, True, color), (x,y))

# Main loop
running = True
emit_timer = 0.0
while running:
    dt = clock.tick(FPS) / 1000.0
    emit_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_w:
                show_wave = not show_wave
            elif event.key == pygame.K_p:
                show_particles = not show_particles
            elif event.key == pygame.K_SPACE:
                emit = True
            elif event.key == pygame.K_c:
                particle_hits.clear()
                particle_counts[:] = 0
            elif event.key == pygame.K_s:
                use_envelope = not use_envelope
                intensity = compute_intensity(slit_separation, wavelength, screen_x_pos, ys, use_envelope)
                cdf = make_cdf(intensity)
            elif event.key == pygame.K_UP:
                wavelength *= 1.1
                k = 2.0 * math.pi / wavelength
                intensity = compute_intensity(slit_separation, wavelength, screen_x_pos, ys, use_envelope)
                cdf = make_cdf(intensity)
            elif event.key == pygame.K_DOWN:
                wavelength /= 1.1
                k = 2.0 * math.pi / wavelength
                intensity = compute_intensity(slit_separation, wavelength, screen_x_pos, ys, use_envelope)
                cdf = make_cdf(intensity)
            elif event.key == pygame.K_RIGHT:
                slit_separation *= 1.1
                intensity = compute_intensity(slit_separation, wavelength, screen_x_pos, ys, use_envelope)
                cdf = make_cdf(intensity)
            elif event.key == pygame.K_LEFT:
                slit_separation /= 1.1
                intensity = compute_intensity(slit_separation, wavelength, screen_x_pos, ys, use_envelope)
                cdf = make_cdf(intensity)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                emit = False

    # continuous emission when SPACE held (or auto small bursts)
    if emit or emit_timer > 1.0:
        # emit a small batch
        to_emit = particles_batch if emit else int(particles_per_second * emit_timer)
        for _ in range(to_emit):
            idx = sample_hit(cdf)
            particle_hits.append(idx)
            particle_counts[idx] += 1
        emit_timer = 0.0

    # draw background
    screen.fill((10, 10, 20))

    # draw slits representation on left
    # represent slits at x coordinate slit_center_x
    # draw screen plane as vertical rectangle on right
    slit_x_draw = slit_center_x
    # slits positions in pixels
    s1_y = int(slit_y_center - slit_separation / 2.0)
    s2_y = int(slit_y_center + slit_separation / 2.0)
    # draw slits
    pygame.draw.rect(screen, (200,200,220), (slit_x_draw-6, s1_y-6, 12, 12))
    pygame.draw.rect(screen, (200,200,220), (slit_x_draw-6, s2_y-6, 12, 12))
    draw_text(screen, "Slits", slit_x_draw-24, int(slit_y_center - slit_separation - 30))

    # draw "screen plane" detector region
    screen_vis_x = slit_center_x + 120
    detector_w = SCREEN_W - screen_vis_x - 20
    pygame.draw.rect(screen, (40,40,60), (screen_vis_x-2, 2, detector_w+4, SCREEN_H-4), 1)

    # draw wave intensity background if enabled
    if show_wave:
        draw_intensity_background(screen, intensity)

    # draw particle hits as small dots on the detector area
    if show_particles:
        # map pixel row index to x within detector region (randomized horizontally for visual scatter)
        for idx in particle_hits[-5000:]:  # draw only recent N for performance
            py = idx
            px = screen_vis_x + random.randint(0, detector_w-1)
            # color based on local intensity for nicer visuals
            b = int(200 * np.clip(intensity[idx], 0.0, 1.0))
            # alpha-like effect by using circle with blend
            try:
                gfxdraw.filled_circle(screen, int(px), int(py), 1, (255, 220, b))
            except Exception:
                pass

        # also draw an accumulated bar graph to the left of detector to show counts
        # normalize counts for drawing
        maxc = max(1, particle_counts.max())
        bar_x = screen_vis_x - 40
        bar_w = 30
        for i in range(rows):
            h_val = particle_counts[i] / maxc
            # draw a tiny horizontal line proportional to counts
            if h_val > 0:
                screen.fill((220, 120, 60), (bar_x, i, int(h_val * bar_w), 1))

    # Overlays and info
    draw_text(screen, f"Wavelength: {wavelength:.2f}   (UP/DOWN)", 10, 10)
    draw_text(screen, f"Slit separation: {slit_separation:.2f}   (LEFT/RIGHT)", 10, 30)
    draw_text(screen, f"Particles emitted: {len(particle_hits)}   (SPACE to emit, C to clear)", 10, 50)
    draw_text(screen, f"Single-slit envelope: {'ON' if use_envelope else 'OFF'} (S to toggle)", 10, 70)
    draw_text(screen, "W: toggle wave view    P: toggle particles    Q/ESC: quit", 10, 90)
    draw_text(screen, f"Showing wave: {show_wave}    Showing particles: {show_particles}", 10, 110)

    pygame.display.flip()

pygame.quit()
sys.exit()
