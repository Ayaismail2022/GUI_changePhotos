import tkinter as tk
from tkinter import Frame, Label, filedialog, ttk, Canvas, BOTH
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import cv2
import numpy as np


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("800x600")
        self.root.configure(bg="#34495e")
        self.original_img = None
        self.current_img = None
        self.zoom_level = 1.0
        self.brightness_level = 1.0
        self.contrast_level = 1.0

        self.main_frame = tk.Frame(self.root, bg="#34495e")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_x = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.panel = self.canvas.create_image(0, 0, anchor=tk.CENTER)

        self.control_frame = tk.Frame(self.root, bg="#2c3e50")
        self.control_frame.pack(fill=tk.X)

        self.create_buttons()
        self.create_sliders()

    def create_buttons(self):
        btn_frame = Frame(self.root, bg="#2c3e50")
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="📂 choose photo", command=self.open_image).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="🎨 Grayscale", command=self.apply_grayscale).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="🌫 Blur", command=self.apply_blur).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="🧱 Edges", command=self.apply_edges).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="🌈 Artistic", command=self.apply_colormap).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="🔃 Flip", command=self.flip_image).grid(row=0, column=5, padx=5)
        ttk.Button(btn_frame, text="🔄 Rotate", command=self.rotate_image).grid(row=0, column=6, padx=5)
        ttk.Button(btn_frame, text="💾 Save", command=self.save_image).grid(row=0, column=7, padx=5)
        ttk.Button(btn_frame, text="🔁 Reset", command=self.reset_all).grid(row=0, column=8, padx=5)

    def create_sliders(self):
        slider_frame = tk.Frame(self.root, bg="#34495e")
        slider_frame.pack(fill=tk.X, pady=10)

        tk.Label(slider_frame, text="Zoom", fg="white", bg="#34495e").pack(side=tk.LEFT)
        self.zoom_slider = ttk.Scale(slider_frame, from_=0.5, to=2.0, value=1.0, command=self.update_zoom, length=200)
        self.zoom_slider.pack(side=tk.LEFT, padx=10)

        tk.Label(slider_frame, text="Brightness", fg="white", bg="#34495e").pack(side=tk.LEFT)
        self.brightness_slider = ttk.Scale(slider_frame, from_=0.5, to=2.0, value=1.0, command=self.update_brightness, length=200)
        self.brightness_slider.pack(side=tk.LEFT, padx=10)

        tk.Label(slider_frame, text="Contrast", fg="white", bg="#34495e").pack(side=tk.LEFT)
        self.contrast_slider = ttk.Scale(slider_frame, from_=0.5, to=2.0, value=1.0, command=self.update_contrast, length=200)
        self.contrast_slider.pack(side=tk.LEFT, padx=10)

    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            img = cv2.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (400, 400))
            self.original_img = Image.fromarray(img)
            self.current_img = self.original_img.copy()
            self.reset_sliders()
            self.update_display()

    def show_image(self):
        if self.current_img is not None:
            img = self.apply_brightness_contrast(self.current_img.copy())
            img = self.apply_zoom(img)
            img_pil = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.panel.config(image=img_tk)
            self.panel.image = img_tk

    def update_display(self):
        img = self.current_img.resize((int(300 * self.zoom_level), int(300 * self.zoom_level)))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.panel, image=self.tk_img)
        self.canvas.coords(self.panel, 400, 300)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def apply_grayscale(self):
        if self.current_img:
            img = self.current_img.convert('L').convert('RGB')
            self.current_img = img
            self.update_display()

    def apply_blur(self):
        if self.current_img:
            self.current_img = self.current_img.filter(ImageFilter.GaussianBlur(radius=4))
            self.update_display()

    def apply_edges(self):
        if self.current_img:
            self.current_img = self.current_img.filter(ImageFilter.FIND_EDGES)
            self.update_display()

    def update_zoom(self, val):
        self.zoom_level = float(val)
        self.update_display()

    def update_brightness(self, val):
        self.brightness_level = float(val)
        if self.original_img:
            enhancer = ImageEnhance.Brightness(self.original_img)
            self.current_img = enhancer.enhance(self.brightness_level)
            self.apply_contrast()

    def update_contrast(self, val):
        self.contrast_level = float(val)
        self.apply_contrast()

    def apply_colormap(self):
        if self.current_img is not None:
            img_np = np.array(self.current_img)
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            colored = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            self.current_img = Image.fromarray(cv2.cvtColor(colored, cv2.COLOR_BGR2RGB))
            self.update_display()

    def rotate_image(self):
        if self.current_img is not None:
            self.current_img = self.current_img.rotate(90, expand=True)
            self.update_display()

    def flip_image(self):
        if self.current_img is not None:
            self.current_img = self.current_img.transpose(Image.FLIP_LEFT_RIGHT)
            self.update_display()

    def apply_contrast(self):
        if self.original_img:
            enhancer = ImageEnhance.Brightness(self.original_img)
            temp_img = enhancer.enhance(self.brightness_level)
            enhancer = ImageEnhance.Contrast(temp_img)
            self.current_img = enhancer.enhance(self.contrast_level)
            self.update_display()

    def reset_all(self):
        if self.original_img:
            self.zoom_level = 1.0
            self.brightness_level = 1.0
            self.contrast_level = 1.0
            self.current_img = self.original_img.copy()
            self.reset_sliders()
            self.update_display()

    def reset_sliders(self):
        self.zoom_slider.set(1.0)
        self.brightness_slider.set(1.0)
        self.contrast_slider.set(1.0)

    def apply_brightness_contrast(self, img):
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(self.brightness_level)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(self.contrast_level)
        return np.array(img)

    def apply_zoom(self, img):
        w, h = img.size
        return img.resize((int(w * self.zoom_level), int(h * self.zoom_level)))

    def save_image(self):
        if self.current_img is not None:
            img_to_save = self.apply_brightness_contrast(self.current_img.copy())
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                    filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
            if save_path:
                save_bgr = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
                cv2.imwrite(save_path, save_bgr)


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
