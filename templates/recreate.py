from PIL import Image, ImageDraw
import numpy as np

# Load the reference image
reference_image_path = 'bitgreenishapple.jpg'  # Replace with your reference image path
reference_image = Image.open(reference_image_path)
canvas_width, canvas_height = reference_image.size

# Create a blank canvas of the same size as the reference image
canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(canvas)

# Define the brush properties
brush_color = (255, 0, 0, 128)  # Red color with transparency
brush_size = 10

# Simulate painting on the canvas
def paint(draw, x, y, color, size):
    draw.ellipse((x - size, y - size, x + size, y + size), fill=color)

# Example coordinates for painting
paint_coordinates = [(100, 100), (150, 150), (200, 200), (250, 250), (300, 300)]

# Paint on the canvas
for coord in paint_coordinates:
    paint(draw, coord[0], coord[1], brush_color, brush_size)

# Convert canvas to a numpy array to highlight pixels
canvas_array = np.array(canvas)

# Highlight the painted pixels by outlining them in a contrasting color
highlight_color = (0, 255, 0, 255)  # Green color for highlighting
for coord in paint_coordinates:
    x, y = coord
    for i in range(-brush_size, brush_size + 1):
        for j in range(-brush_size, brush_size + 1):
            if 0 <= x + i < canvas_width and 0 <= y + j < canvas_height:
                distance = np.sqrt(i*2 + j*2)
                if brush_size - 1 < distance < brush_size + 1:
                    canvas_array[y + j, x + i] = highlight_color

# Convert the numpy array back to an image
highlighted_canvas = Image.fromarray(canvas_array)

# Overlay the highlighted canvas on the reference image
highlighted_reference_image = Image.alpha_composite(reference_image.convert('RGBA'), highlighted_canvas)

# Save the resulting image
highlighted_reference_image.save('highlighted_reference_image.png')

# Show the resulting image
highlighted_reference_image.show()