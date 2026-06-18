import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from models import Pokemon, PokemonList, Region, Game
from data.constants import SHINY_LOCKED, GAMES_TO_MAX_REGION_MAPPING

def _add_subregions(region: Region):
    region_filter_in: list[Region] = [region]
    if region.name + "_VARIANTS" in Region.__members__:
        region_filter_in += [Region[region.name + "_VARIANTS"]]

    if region.name == "ALOLA":
        region_filter_in += [Region.UNKNOWN]
    elif region.name == "PALDEA":
        region_filter_in += [Region.KITAKAMI, Region.BLUEBERRY, Region.LUMIOSE]
    region_filter_in = sorted(region_filter_in, key=lambda r: r.value)

    return region_filter_in


class GUI:
    def __init__(self, root: tk.Tk, data: PokemonList):
        self.root = root
        self.data: PokemonList = data
        self.active_data: PokemonList = data
        self.shiny_mode_toggle = tk.BooleanVar(value=False)

        # initialize screen containers
        self.menu_frame = tk.Frame(root)
        self.checklist_frame = tk.Frame(root)
        self.stats_frame = tk.Frame(root)
        self.missing_frame = tk.Frame(root)

        # display main menu
        self.setup_menu_screen()
        self.menu_frame.pack(padx=20, pady=20)


    def setup_menu_screen(self):
        menu_title = tk.Label(self.menu_frame, text="Pokemon Living Dex Organizer", font=("Arial", 24, "bold"))
        menu_title.pack(pady=10)

        shiny_mode_checkbox = tk.Checkbutton(
            self.menu_frame,
            text="Shiny Mode",
            variable=self.shiny_mode_toggle,
            command=self.toggle_shiny_mode(),
            font=("Arial", 16)
        )
        shiny_mode_checkbox.pack(pady=10)

        master_list_button = tk.Button(
            self.menu_frame,
            text="Full Living Dex",
            command=lambda: self.start_checklist(None),
            font=("Arial", 16),
            padx=10, pady=5
        )
        master_list_button.pack(pady=10)

        region_grid_frame = tk.Frame(self.menu_frame)
        region_grid_frame.pack(pady=10)

        exclude_regions = ["UNKNOWN", "KITAKAMI", "BLUEBERRY", "LUMIOSE"]
        region_list = [region for region in Region if "VARIANT" not in region.name and all(r not in region.name for r in exclude_regions)]

        for i, region in enumerate(region_list):
            row = i//5
            col = i%5

            region_filter_in = _add_subregions(region)

            region_button = tk.Button(
                region_grid_frame,
                text=region.name[0] + region.name[1:].lower(),
                command=lambda f=region_filter_in: self.start_checklist(f), # grab region filter on button creation
                font=("Arial", 16),
                padx=10, pady=5
            )
            region_button.grid(row=row, column=col, padx=6, pady=6)

        stats_button = tk.Button(
            self.menu_frame,
            text="View All Statistics",
            command=self.show_stats,
            font=("Arial", 16),
            padx=10, pady=5
        )
        stats_button.pack(pady=10)

    def start_checklist(self, region_filter: list[Region] | None):
        """Load boxes for selected region based on filter param"""
        # hide menu
        self.menu_frame.pack_forget()

        # clear old checklist, allows switching between
        for widget in self.checklist_frame.winfo_children():
            widget.destroy()

        self.apply_region_filter(region_filter)

        self.page_numbers = [x + 1 for x in range(len(self.active_data.boxes))]
        self.current_page = tk.StringVar(value="1")
        self.checkbox_vars = []

        self.render_fn = self.show_page

        self.title_label = tk.Label(self.checklist_frame, text="")
        self.title_label.pack()

        self.page_dropdown = ttk.Combobox(
            self.checklist_frame,
            textvariable=self.current_page,
            values=self.page_numbers,
            state="readonly",
        )
        self.page_dropdown.pack()
        self.page_dropdown.bind("<<ComboboxSelected>>", self.on_page_change)

        self.page_frame = tk.Frame(self.checklist_frame)
        self.page_frame.pack()

        self.prev_button = tk.Button(self.checklist_frame, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_button = tk.Button(self.checklist_frame, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.submit_button = tk.Button(self.checklist_frame, text="Submit", command=self.submit_results)
        self.submit_button.pack(pady=5)

        self.menu_button = tk.Button(self.checklist_frame, text="Return to Menu", command=self.return_to_menu)
        self.menu_button.pack(pady=5)

        self.checklist_frame.pack(padx=10, pady=10)
        self.show_page()


    def show_stats(self):
        self.menu_frame.pack_forget()
        self.missing_frame.pack_forget()

        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # create a canvas and scrollbar inside the main page frame
        canvas = tk.Canvas(self.stats_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.stats_frame, orient="vertical", command=canvas.yview)
        
        scrollable_inner_frame = tk.Frame(canvas)

        scrollable_inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind(
            "<Configure>", 
            lambda event: canvas.itemconfig(canvas_window, width=event.width)
        )

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        self.title_label = tk.Label(scrollable_inner_frame, text="Living Dex Completion Stats", font=("Arial", 24, "bold"))
        self.title_label.pack()

        self.gen_title_label = tk.Label(scrollable_inner_frame, text="By Generation:", font=("Arial", 16))
        self.gen_title_label.pack()

        exclude_regions = ["UNKNOWN", "KITAKAMI", "BLUEBERRY", "LUMIOSE"]
        region_list = [region for region in Region if "VARIANT" not in region.name and all(r not in region.name for r in exclude_regions)]

        style = ttk.Style()
        style.theme_use('clam')  # Allows custom colors on Windows/Mac/Linux
        style.configure("Green.Horizontal.TProgressbar", background="#2ECC71", troughcolor="#E5E7E9")
        style.configure("Blue.Horizontal.TProgressbar", background="#3498DB", troughcolor="#E5E7E9")
        style.configure("Red.Horizontal.TProgressbar", background="#F54927", troughcolor="#E5E7E9")

        self.total_title_label = tk.Label(scrollable_inner_frame, text="Total:", font=("Arial", 16))
        self.total_title_label.pack()
        
        # display total stats
        self.display_stats(scrollable_inner_frame, "Green.Horizontal.TProgressbar", "TOTAL", None, None)
        
        # display stats by region
        for region in region_list:
            region_filter_in = _add_subregions(region)
            self.display_stats(scrollable_inner_frame, "Blue.Horizontal.TProgressbar", region.name, region_filter_in, None)

        self.game_title_label = tk.Label(scrollable_inner_frame, text="By Game:", font=("Arial", 16))
        self.game_title_label.pack()

        # display stats by game
        for game in GAMES_TO_MAX_REGION_MAPPING:
            self.display_stats(scrollable_inner_frame, "Red.Horizontal.TProgressbar", Game[game].value, None, Game[game])

        self.menu_button = tk.Button(scrollable_inner_frame, text="Return to Menu", command=self.return_to_menu, font=("Arial", 12))
        self.menu_button.pack(pady=5)

        self.stats_frame.pack(padx=10, pady=10, fill="both", expand=True)


    def display_stats(self, frame: tk.Frame, color_str: str, label_name: str, region_filter: list[Region] | None, game_filter: Game | None):
        self.missing_frame.pack_forget()

        completion_count, total, missing = self.data.calculate_completion_stats(self.shiny_mode_toggle.get(), region_filter, game_filter)
        percentage = completion_count * 100 / total if total > 0 else 0

        name_label = tk.Label(frame, text=label_name, font=("Arial", 12, "bold"))
        name_label.pack(padx=10, pady=(15, 2))

        stat_label = tk.Label(frame, text=f"{completion_count} / {total} ({percentage: .1f}%)", font=("Arial", 10))
        stat_label.pack(padx=10, pady=(0, 5))

        missing_button = tk.Button(
            frame, 
            text="Show Missing", 
            command=lambda f=missing: self.start_missing(f),
            font=("Arial", 12)
        )
        missing_button.pack(padx=10, pady=(0, 5))

        progress_bar = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=600,
            mode="determinate",
            style=color_str
        )
        progress_bar.pack(padx=10, pady=10)
        progress_bar['value'] = percentage


    def start_missing(self, missing: PokemonList):
        """Load boxes for selected region based on filter param"""
        # hide menu
        self.stats_frame.pack_forget()

        # clear old missing page, allows switching between
        for widget in self.missing_frame.winfo_children():
            widget.destroy()

        self.page_numbers = [x + 1 for x in range(len(missing.boxes))]
        self.current_page = tk.StringVar(value="1")
        self.checkbox_vars = []

        self.active_missing_data = missing
        self.render_fn = self.show_missing

        self.title_label = tk.Label(self.missing_frame, text="")
        self.title_label.pack()

        self.page_dropdown = ttk.Combobox(
            self.missing_frame,
            textvariable=self.current_page,
            values=self.page_numbers,
            state="readonly",
        )
        self.page_dropdown.pack()
        self.page_dropdown.bind("<<ComboboxSelected>>", self.on_page_change)

        self.missing_page_frame = tk.Frame(self.missing_frame)
        self.missing_page_frame.pack()

        self.prev_button = tk.Button(self.missing_frame, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_button = tk.Button(self.missing_frame, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.menu_button = tk.Button(self.missing_frame, text="Return to Stats", command=self.show_stats)
        self.menu_button.pack(pady=5)

        self.missing_frame.pack(padx=10, pady=10)
        self.show_missing()


    def show_missing(self):
        """Render missing Pokemon images and names in grid format"""
        for widget in self.missing_page_frame.winfo_children():
            widget.destroy()

        # pre-allocate space for columns to handle empty spaces
        for col in range(6):
            self.missing_page_frame.grid_columnconfigure(
                col, 
                weight=1, 
                minsize=150,
                uniform="box_cols"
            )

        # pre-allocate space for row contents (images, names) to handle empty spaces
        for r in range(10):
            if r % 2 == 0:
                # pokemon images
                self.missing_page_frame.grid_rowconfigure(r, weight=1, uniform="img_rows")
            else:
                # pokemon names
                self.missing_page_frame.grid_rowconfigure(r, weight=1, uniform="lbl_rows")


        box_data: list[list[Pokemon]] = self.active_missing_data.boxes[
            self.get_current_page() - 1
        ]  # 0-29
        self.title_label.config(text=f"BOX {self.get_current_page()}")

        for i, row in enumerate(box_data):
            for j, item in enumerate(row):
                item_label = tk.Label(
                    self.missing_page_frame,
                    text=item,
                    width=14,
                    height=2,
                    wraplength=100,
                    justify="center"
                )

                # image path ends with "_n" for normal and "_r" for shiny (rare). leave shiny locked pokemon as shiny locked
                if item.name in SHINY_LOCKED:
                    item.image_path = item.image_path.replace("_r.png", "_n.png")
                elif self.shiny_mode_toggle.get():
                    item.image_path = item.image_path.replace("_n.png", "_r.png")
                else:
                    item.image_path = item.image_path.replace("_r.png", "_n.png")

                image = Image.open(item.image_path)
                image = image.resize((50, 50), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(self.missing_page_frame, image=photo)
                image_label.image = photo

                image_label.grid(row=2 * i, column=j, padx=5, pady=5)
                item_label.grid(row=2 * i + 1, column=j, padx=5, pady=5)


    def return_to_menu(self):
        """Return from checklist or stats pages to menu"""
        self.checklist_frame.pack_forget()
        self.stats_frame.pack_forget()
        self.menu_frame.pack(padx=20, pady=20)


    def show_page(self):
        """Render the Pokemon images, names, and checkboxes in grid format"""
        for widget in self.page_frame.winfo_children():
            widget.destroy()

        # pre-allocate space for columns to handle empty spaces
        for col in range(6):
            self.page_frame.grid_columnconfigure(
                col, 
                weight=1, 
                minsize=150,
                uniform="box_cols"
            )

        # pre-allocate space for row contents (images, names, checkboxes) to handle empty spaces
        for r in range(15):
            if r % 3 == 0:
                # pokemon images
                self.page_frame.grid_rowconfigure(r, weight=1, uniform="img_rows")
            elif r % 3 == 1:
                # pokemon names
                self.page_frame.grid_rowconfigure(r, weight=1, uniform="lbl_rows")
            else:
                # checkboxes
                self.page_frame.grid_rowconfigure(r, weight=1, uniform="chk_rows")

        box_data: list[list[Pokemon]] = self.active_data.boxes[
            self.get_current_page() - 1
        ]  # 0-29
        self.title_label.config(text=f"BOX {self.get_current_page()}")

        self.checkbox_vars = []

        for i, row in enumerate(box_data):
            for j, item in enumerate(row):
                item_label = tk.Label(
                    self.page_frame,
                    text=item,
                    width=14,
                    height=2,
                    wraplength=100,
                    justify="center"
                )

                # image path ends with "_n" for normal and "_r" for shiny (rare). leave shiny locked pokemon as shiny locked
                if item.name in SHINY_LOCKED:
                    item.image_path = item.image_path.replace("_r.png", "_n.png")
                elif self.shiny_mode_toggle.get():
                    item.image_path = item.image_path.replace("_n.png", "_r.png")
                else:
                    item.image_path = item.image_path.replace("_r.png", "_n.png")

                image = Image.open(item.image_path)
                image = image.resize((50, 50), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(self.page_frame, image=photo)
                image_label.image = photo

                checkbox_var = tk.IntVar(value=int(item.have))
                self.checkbox_vars.append((item, checkbox_var))
                checkbox = tk.Checkbutton(self.page_frame, variable=checkbox_var)

                image_label.grid(row=3 * i, column=j, padx=5, pady=5)
                item_label.grid(row=3 * i + 1, column=j, padx=5, pady=5)
                checkbox.grid(row=3 * i + 2, column=j, padx=5, pady=5)


    def on_page_change(self, event):
        self.render_fn()


    def show_previous(self):
        active_page = self.get_current_page()
        if active_page > 1:
            self.set_current_page(active_page - 1)
            self.render_fn()
        elif active_page == 1:
            self.set_current_page(len(self.page_numbers))
            self.render_fn()


    def show_next(self):
        active_page = self.get_current_page()
        if active_page < len(self.page_numbers):
            self.set_current_page(active_page + 1)
            self.render_fn()
        elif active_page == len(self.page_numbers):
            self.set_current_page(1)
            self.render_fn()


    def submit_results(self):
        for item, var in self.checkbox_vars:
            item.have = var.get()

        self.data.save_to_json()


    def toggle_shiny_mode(self):
        self.shiny_mode_toggle.get()


    def get_current_page(self):
        return int(self.current_page.get())


    def set_current_page(self, val: int):
        self.current_page.set(str(val))

    
    def apply_region_filter(self, region_filter: list[Region]):
        # need to either filter by region or activate full set
        if region_filter:
            sublist = PokemonList()
            # important - clear out sublist before filtering
            sublist.clear()
            sublist = self.data.filter_by_region(region_filter)

            self.active_data = sublist
        else:
            self.active_data = self.data
            self.active_data.init_boxes()
