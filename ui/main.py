from tkinter import *
import customtkinter as ct
import os
from PIL import Image
from threading import Timer
from tkinter import filedialog as fd


class ScrollableLabelButtonFrame(ct.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.button_list = []

    def add_item(self, item):
        button = ct.CTkButton(self, text=item, height=24, width=240)
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        button.grid(row=len(self.button_list), column=0, pady=(0, 10), padx=5,)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in self.button_list:
            if item == label.cget("text"):
                button.destroy()
                self.button_list.remove(button)
                return

class App(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("S2D")
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        # Left rail
        self.left_rail = ct.CTkFrame(self, width=300, corner_radius=4)
        self.left_rail.columnconfigure(0)
        self.left_rail.rowconfigure(0)
        self.left_rail.rowconfigure(1, weight=1)
        self.left_rail.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        app_label = ct.CTkLabel(self.left_rail, text="History", height=30, font=("Verdana", 25))
        app_label.grid(row=0, column=1, padx=15, pady=15)

        # create scrollable label and button frame
        self.digitized_diagrams = ScrollableLabelButtonFrame(master=self.left_rail, width=300,
                                                                        command=self.label_button_frame_event,
                                                                         fg_color="transparent",
                                                                        corner_radius=0)
        self.digitized_diagrams.grid(row=1, column=1, padx=0, pady=20, sticky="nsew")
        self.digitized_diagrams.grid_forget()

        self.no_history_label = ct.CTkLabel(self.left_rail, text="No digitized diagrams")
        self.no_history_label.grid(row=1, column=1, padx=0, pady=20, sticky="nsew")

        self.upload_button = ct.CTkButton(self.left_rail, height=40, text="Upload diagram", fg_color="#008000", hover_color='#004d00', command=self.upload_image)
        self.upload_button.grid(row=2, column=1, padx=30, pady=30, sticky="nsew")


        # Right rail

        # Right rail top
        self.right_rail = ct.CTkFrame(master=self, corner_radius=4, fg_color="transparent")
        self.right_rail.grid(row=0, column=2, padx=(7.5, 15), pady=15, sticky="nsew")
        self.right_rail.grid_rowconfigure(1, weight=1)
        self.right_rail.grid_columnconfigure(0, weight=1)

        self.right_rail_top = ct.CTkFrame(master=self.right_rail, height=50)
        self.right_rail_top.grid(row=0, column=0, padx=0, pady=(0, 7.5), sticky="nsew")

        self.diagram_path = ct.CTkLabel(master=self.right_rail_top, height=50)

        self.progress_bar = ct.CTkProgressBar(self.right_rail_top, width=150, mode='indeterminate')
        # self.progress_bar.grid(row=0, column=0, padx=15, pady=0)

        self.progress_label = ct.CTkLabel(self.right_rail_top, text="Converting...", height=50)
        # self.progress_label.grid(row=0, column=1)

        # Right rail bottom
        self.right_rail_bottom = ct.CTkFrame(master=self.right_rail)
        self.right_rail_bottom.grid(row=1, column=0, padx=0, pady=(7.5, 0), sticky="nsew")

        self.diagram_preview = ct.CTkLabel(self.right_rail_bottom, text="")
    def label_button_frame_event(self, item):
        print(f"label button frame clicked: {item}")

    def upload_image(self):
        filename = fd.askopenfilename()

        if not bool(filename.strip()):
            return

        self.diagram_path.grid(row=0, column=0, padx=15)
        self.diagram_path.configure(text=filename)

        max_width = 500
        diagram_img = PhotoImage(file=filename)

        original_width = diagram_img.width()
        original_height = diagram_img.height()

        # Calculate the aspect ratio
        aspect_ratio = original_width / original_height

        # Calculate the new height based on the maximum width
        new_width = min(original_width, max_width)
        new_height = int(new_width / aspect_ratio)

        # Resize the image using subsample
        diagram_img = diagram_img.subsample(original_width // new_width, original_height // new_height)

        self.diagram_preview.configure(image=diagram_img)
        self.diagram_preview.grid(row=0, column=0, padx=15, pady=15)

        print(filename)


def truth():
    print("Python rocks!")

if __name__ == "__main__":
    ct.set_appearance_mode("dark")
    app = App()
    app.geometry('1366x640')
    app.resizable(False, False)
    app.mainloop()
