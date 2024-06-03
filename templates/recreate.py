import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageOps
import numpy as np
import os

class InteractiveCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Canvas")

        # Load images
        self.images = [
            "static/banana_original.png",
            "static/banana_segmented.png"
        ]
        self.current_image_index = 0
        self.painted_pixels = []
        self.brush_size = 10
        self.color = "#000000"

        # Load segmented image for comparison
        self.segmented_img = Image.open("static/banana_segmented.png")
        self.segmented_img_data = np.array(self.segmented_img)

        # Set up canvas
        self.canvas = tk.Canvas(root, width=500, height=400, bg="white")
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.start_paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop_paint)
        self.canvas.bind("<B1-Motion>", self.paint)

        # Load the initial image onto the canvas
        self.load_image(self.images[self.current_image_index])

        # Set up color palette
        self.palette_frame = tk.Frame(root)
        self.palette_frame.pack(side=tk.LEFT)
        colors = [
            '#D2A627', '#DDAB11', '#E0BB47', '#EDBF1E', '#F3CD3A',
            '#F6D96A', '#F7D551', '#F8E280', '#FAE4A3', '#FCEDC1',
            '#FEFEFE', '#000000'
        ]
        for color in colors:
            color_button = tk.Button(self.palette_frame, bg=color, width=2, height=1, command=lambda col=color: self.set_color(col))
            color_button.pack(side=tk.TOP, pady=2)

        # Set up brush size toggle
        self.brush_button = tk.Button(root, text="Brush", command=self.toggle_brush_size)
        self.brush_button.pack(side=tk.LEFT, padx=10)

        # Set up similarity info
        self.similarity_label = tk.Label(root, text="Similarity: 0%")
        self.similarity_label.pack(side=tk.LEFT, padx=10)

    def load_image(self, path):
        self.image = Image.open(path)
        self.image = self.image.resize((500, 400), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def change_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.load_image(self.images[self.current_image_index])

    def set_color(self, col):
        self.color = col

    def toggle_brush_size(self):
        self.brush_size = 5 if self.brush_size == 10 else 10
        self.brush_button.config(text="Flat Brush" if self.brush_size == 10 else "Brush")

    def start_ppaint(self, event):
        self.painting = True
        self.paint(event)

    def stop_paint(self, event):
        self.painting = False

    def paint(self, event):
        if not self.painting:
            return

        x, y = event.x, event.y
        self.canvas.create_oval(
            x - self.brush_size, y - self.brush_size,
            x + self.brush_size, y + self.brush_size,
            fill=self.color, outline=self.color
        )
        self.painted_pixels.append((x, y, self.color))
        self.calculate_similarity()

    def calculate_similarity(self):
        if not self.painted_pixels:
            return

        total_difference = 0
        for x, y, color in self.painted_pixels:
            grid_x = x // self.brush_size
            grid_y = y // self.brush_size
            segmented_color = self.segmented_img_data[y, x]
            painted_color = self.canvas.winfo_rgb(color)
            painted_color = tuple(int(val / 256) for val in painted_color)

            difference = np.sqrt(
                (painted_color[0] - segmented_color[0])**2 +
                (painted_color[1] - segmented_color[1])**2 +
                (painted_color[2] - segmented_color[2])**2
            )
            total_difference += difference

        average_difference = total_difference / len(self.painted_pixels)
        similarity = (1 - average_difference / 255) * 100
        self.similarity_label.config(text=f"Similarity: {similarity:.2f}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveCanvasApp(root)
    root.mainloop()
