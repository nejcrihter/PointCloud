import struct

import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

display = (800, 600)
s_value = 0.1

def read_splats_from_file(file_path):
    splats = []
    with open(file_path, "rb") as file:
        while True:
            data = file.read(32)  # Each splat is 32 bytes
            if len(data) < 32:
                break

            position = struct.unpack('fff', data[:12])
            scale = struct.unpack('fff', data[12:24])
            color = struct.unpack('BBBB', data[24:28])  # RGBA color
            rotation = struct.unpack('BBBB', data[28:32])  # Quaternion rotation
            color_normalized = [c / 255.0 for c in color[:3]] + [color[3] / 255.0]
            splats.append((position, scale, color_normalized, rotation))
    return splats

def init(display):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(2, 1, 3, -0.5, -1, 0, 0, 1, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)

def transform_points(splats, mvp_matrix):
    viewport = np.array([0, 0, display[0], display[1]])
    out_splats = []

    for position, scale, color, rotation in splats:
        screen_pos = world_to_screen(position, mvp_matrix, viewport)
        out_splats.append((screen_pos, scale, color, rotation, position))

    return out_splats


def world_to_screen(position, mvp_matrix, viewport):
    pos_h = np.array(position + (1,), dtype=np.float32)  # Convert to homogeneous coordinates

    # Transform position to clip space
    clip_space_pos = mvp_matrix @ pos_h

    # Perspective division to get normalized device coordinates (NDC)
    ndc_space_pos = clip_space_pos[:3] / clip_space_pos[3]

    # Map from NDC to viewport (screen) coordinates
    screen_x = ((ndc_space_pos[0] + 1) / 2.0) * viewport[2] + viewport[0]
    screen_y = ((1 - ndc_space_pos[1]) / 2.0) * viewport[3] + viewport[1]
    screen_z = ndc_space_pos[2] * 0.5 + 0.5

    return (screen_x / display[0], screen_y / display[1], screen_z)

def render_splats(splats):
    # glPointSize(1)  # Size of the points
    glBegin(GL_POINTS)
    for position, scale, color, rotation, a in splats:
        glColor4f(color[0], color[1], color[2], color[3])  # Use RGBA
        glVertex3fv(position)
    glEnd()


def init_pygame_and_opengl(window_size):
    pygame.init()
    pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)

def main():
    pygame.init()
    init_pygame_and_opengl(display)

    modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
    MVP_matrix = np.dot(modelview_matrix, projection_matrix)

    splats = read_splats_from_file('nike.splat')
    transformed_splats = transform_points(splats, MVP_matrix)
    init(display)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            render_splats(transformed_splats)
            pygame.display.flip()
            print('rendering')
            pygame.time.wait(10)

if __name__ == "__main__":
    main()
