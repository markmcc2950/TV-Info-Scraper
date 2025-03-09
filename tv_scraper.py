import requests
import tkinter as tk
from tkinter import ttk, font

class TVMazeApp:
    # To be retrieved once the root is created
    screen_width = 0
    screen_height = 0

    # The actual window size we'll display (as a square)
    window_size = 1000
    button_w = 100
    button_h = 50

    json_results_show = None
    json_results_season = None
    show_picked = ""
    show_id_picked = -1
    season_picked = -1
    episode_picked = -1

    shows_found = 0

    def __init__(self, root):
        self.root = root
        self.root.title("TV Show Information")
        self.root.config(bg="gray20")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        
        # Set how and where the window will appear on screen
        self.window_size = (self.screen_height * 4) // 5
        position_top = (self.screen_height // 2)
        position_left = (self.screen_width // 2) - (self.window_size)

        # Set button sizes properly now
        self.button_w = int(self.window_size / 10)
        self.button_h = int(self.window_size / 40) * 0.8

        if self.window_size < 500:
            self.window_size = 500

        self.root.geometry(f"{self.window_size}x{self.window_size}+{position_top}+{position_left}")
        self.root.resizable(False, False)

        # Set up Frames for Results and Actor Data
        self.results_frame = tk.Frame(self.root, background="gray20")
        self.results_frame.place(x=0, y=0, width=int((self.window_size * 3) / 4), height=self.window_size)

        self.info_frame = tk.Frame(self.root, background="gray10")
        self.info_frame.place(x=0, y=int(((self.window_size * 3) / 4) + (self.window_size / 100)), width=int((self.window_size * 3) / 4), height=int(((self.window_size) / 4)))

        self.text_frame = tk.Frame(self.root, background="gray20")
        self.text_frame.place(
            x=((self.window_size) * 0.01), 
            y=((self.window_size) / 10) - (1.1 * self.button_h), 
            width=self.button_w * 7, 
            height=self.button_h
        )

        # Define the font for the list of shows found
        my_font = font.Font(family="Helvetica", size=(int(self.window_size / 75)), weight="bold", slant="roman")

        # Set up the Listbox with a font size
        self.show_list = tk.Listbox(self.root, bg="gray10", font=my_font, foreground="white")
        self.show_list.place(x=int(self.window_size - (self.window_size * 0.26)), y=self.window_size * 0.01, width=int(self.window_size / 4), height=int((self.window_size * 1) / 3))

        # Bind the <<ListboxSelect>> event to automatically fetch seasons when a show is selected
        self.show_list.bind("<<ListboxSelect>>", self.on_show_select)

        # Set up the Text Entry Widget
        self.entry = tk.Entry(root)
        self.entry.configure(justify="left")
        self.entry.place(x=self.window_size - ((self.window_size) * 0.4), y=self.window_size * 0.01, width=self.button_w * 1.25, height=self.button_h)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.on_enter_pressed)

        # Set up the Search Button
        self.search_button = tk.Button(root, text="Search", command=self.search_show)
        self.search_button.place(x=(self.window_size - (self.window_size * 0.33)) - (self.button_w * 1.25), y=self.window_size * 0.01, width=self.button_w / 2, height=self.button_h)

        self.actor_frame = tk.Frame(root)

        self.actor_data = {}

    def on_enter_pressed(self, event):
        self.search_show()

    def search_show(self):
        show_name = self.entry.get()
        if not show_name:
            return

        url = f"https://api.tvmaze.com/search/shows?q={show_name}"
        response = requests.get(url)

        if response.status_code == 200:
            results = response.json()
            self.json_results_show = response
            self.show_list.delete(0, tk.END)
            self.show_data = {}
            self.stored_show_name = {}

            if len(results) == 1:
                # If only one result, auto-select it and fetch seasons
                show = results[0]['show']
                self.show_picked = show['name']
                self.show_list.insert(0, show['name'])
                self.selected_show_id = show['id']
                self.show_id_picked = show['id']
                self.get_seasons()  # This will fetch and display the seasons without clearing the frame again
            else:
                # Populate the list normally
                for index, item in enumerate(results):
                    show = item['show']
                    list_font = font.Font(family="Helvetica", size=int((self.window_size / 75)), weight="bold", slant="roman")
                    self.show_list.configure(font=list_font)
                    self.show_list.insert(index, show['name'])
                    self.show_data[index] = show['id']
                    self.stored_show_name[index] = show['name']

    def on_show_select(self, event):
        # When a show is selected, fetch its seasons
        selected_index = self.show_list.curselection()

        # Check if we have a valid selectino before doing anything
        if selected_index:
            selected_index = selected_index[0]
            if selected_index in self.show_data:
                self.show_picked = self.stored_show_name[selected_index]
                show_id = self.show_data[selected_index]
                self.selected_show_id = show_id

                # Clear only if the show wasn't already loaded
                if not hasattr(self, 'seasons_loaded') or not self.seasons_loaded:
                    self.clear_frame(self.results_frame)
                    self.clear_frame(self.info_frame)
                    self.clear_frame(self.text_frame)
                    self.get_seasons()
            else:
                print(f"Selected index {selected_index} not found in show_data.")
        else:
            print("No show selected.")

    def get_seasons(self):
        url = f"https://api.tvmaze.com/shows/{self.selected_show_id}/seasons"
        response = requests.get(url)

        if response.status_code == 200:
            self.json_results_season = response
            self.clear_frame(self.results_frame)
            self.clear_frame(self.info_frame)
            self.clear_frame(self.text_frame)
            seasons = response.json()

            iterator = -1

            # Set the font to scale with the length of the show name
            default_label_font = font.Font(family="Helvetica", size=14 , weight="bold", underline=True)
            name_length = default_label_font.measure(self.show_picked)            
            default_label_font.configure(size=14 - (name_length // 50) if name_length > 100 else 14)

            label = tk.Label(
                self.text_frame, 
                text=f"{len(seasons)} Seasons For {self.show_picked}", 
                font=default_label_font,
                background="grey20",
                foreground="white")
            label.place(
                x=(((self.window_size * 2) / 16) - self.button_w) + (1.1 * self.button_w * int(iterator / 22)), 
                y=0, 
                width=self.button_w * 3, 
                height=self.button_h
            )
            for season in seasons:
                iterator += 1
                button = tk.Button(
                    self.results_frame,
                    text=f"Season {season['number']}",
                    command=lambda s_id=season['id']: self.get_episodes(s_id),
                )
                button.place(
                    x=(((self.window_size * 2) / 16) - self.button_w) + (1.1 * self.button_w * int(iterator / 22)), 
                    y=((self.window_size) / 10) + (1.1 * self.button_h * 1.25) * (iterator % 22), 
                    width=self.button_w, 
                    height=self.button_h * 1.25
                )
    
    def get_season_number(self, season_id, seasons_response):
        if seasons_response is not None:
            seasons = seasons_response.json()

            # Search for the season that matches the given season_id
            season = next((s for s in seasons if s["id"] == season_id), None)

            if season:
                return season["number"]  # Return the season number (e.g., 2)
            else:
                print(f"Season ID {season_id} not found.")
                return None
        else:
            print("Seasons response is None.")
            return None



    def get_top_episodes_of_season(self, show_id, season_number, season_id, seasons_response, top_n=5):           
        # Ensure we have valid show data
        if self.json_results_show is not None:
            show_data = self.json_results_show.json()
        else:
            # Fetch show details manually if not already stored
            show_url = f"https://api.tvmaze.com/shows/{show_id}"
            show_response = requests.get(show_url)

            if show_response.status_code == 200:
                show_data = show_response.json()
                self.json_results_show = show_response
            else:
                print(f"Failed to fetch show details for ID {show_id}.")
                return []

        if isinstance(show_data, list) and show_data:
            show_name = show_data[0]['show']['name']
        else:
            show_name = "Unknown Show"

        if seasons_response is not None: 
            seasons = seasons_response.json()
            
            if not season_id:
                print(f"Season {season_number} not found for show '{show_name}'.")
                return []

            episodes_url = f"https://api.tvmaze.com/seasons/{season_id}/episodes"
            episodes_response = requests.get(episodes_url)

            if episodes_response.status_code == 200:
                episodes = episodes_response.json()

                sorted_episodes = sorted(episodes, key=lambda e: e['rating']['average'] or 0, reverse=True)

                for ep in sorted_episodes:
                    ep["show_name"] = show_name  # Keep the correct show association

                return sorted_episodes[:top_n]

        print("Failed to fetch data.")
        return []


    def get_episodes(self, season_id):
        url = f"https://api.tvmaze.com/seasons/{season_id}/episodes"
        response = requests.get(url)

        if response.status_code == 200:
            # Get the top 3 episodes of the season to highlight when we make the buttons
            season_number = self.get_season_number(season_id, self.json_results_season)
            top_episodes = self.get_top_episodes_of_season(self.show_id_picked, season_number, season_id, response, 3)
            top_episode = top_episodes[0]

            self.season_picked = season_number
            self.clear_frame(self.results_frame)
            self.get_seasons()
            episodes = response.json()

            iterator = -1

            # Set the font to scale with the length of the show name
            default_label_font = font.Font(family="Helvetica", size=14 , weight="bold", underline=True)
            name_length = default_label_font.measure(self.show_picked)            
            default_label_font.configure(size=14 - (name_length // 50) if name_length > 100 else 14)
            label = tk.Label(
                self.text_frame, 
                text=f"{len(episodes)} Episodes For Season {self.season_picked}", 
                font=default_label_font,
                background="grey20",
                foreground="white"
            )
            label.place(
                x=int((self.window_size * 8) / 16) - (1.25 * self.button_w), 
                y=0, 
                width=self.button_w * 3, 
                height=self.button_h
            )

            for episode in episodes:
                base_font = font.Font(family="Helvetica", size=12)
                name_length = base_font.measure(episode['name'])
                base_font.configure(size=12 - (name_length // 60) * (1000 // self.window_size) if name_length > 175 else 12)

                iterator += 1
                button_color = "white"
                for ep in top_episodes:
                    if ep["name"] == episode["name"]:
                        if top_episode["name"] == episode["name"]:
                            button_color = "gold"
                        else:
                            button_color = "green"
                button = tk.Button(
                    self.results_frame, 
                    text=f"{episode['name']} ({episode['rating']['average']})",
                    command=lambda e_id=episode['id']: self.show_episode_details(e_id), 
                    wraplength=250,
                    font=base_font,
                    background=button_color,
                    anchor="e"
                )
                button.place(
                    x=int((self.window_size * 8) / 16) - self.button_w, 
                    y=((self.window_size) / 10) + (1.1 * self.button_h) * iterator, 
                    width=int(self.button_w * 2.5), 
                    height=self.button_h
                )

    def show_episode_details(self, episode_id):
        self.episode_picked = episode_id

        episode_url = f"https://api.tvmaze.com/episodes/{episode_id}"
        show_cast_url = f"https://api.tvmaze.com/shows/{self.selected_show_id}/cast"

        episode_response = requests.get(episode_url)
        # cast_response = requests.get(show_cast_url)

        if episode_response.status_code == 200:
            self.clear_frame(self.info_frame)
            episode = episode_response.json()

            def clean_word(word):
                return word.replace('<p>', '').replace('</p>', '')
            # print([clean_word(word) for word in my_string.split()])
            episode_summary = episode['summary']
            summary_string = ' '.join(clean_word(word) for word in episode_summary.split())

            detail_font = font.Font(family="Helvetica", size=(12 - (len(summary_string) // 100) * (1000 // self.window_size)), weight="bold", slant="roman")
            details = f"Title: {episode['name']}\n\nSummary: {summary_string}\n\n" \
                      f"Rating: {episode['rating']['average']}\n\nAir Date: {episode['airdate']}\n\n"
            label = tk.Label(self.info_frame, text=details, justify="left", wraplength=550, anchor="w", font=detail_font)
            label.place(
                x=int(self.window_size / 100), 
                y=int(self.window_size / 100), 
                width=int(((self.window_size * 3) / 4) - (self.window_size / 50)), 
                height=int((((self.window_size) / 4) - (self.window_size / 35)))
            )
            # int((self.window_size * 3) / 4)
            # button.place(x=int((self.window_size * 3) / 16) - self.button_w, y=((self.window_size) / 10) + (1.1 * self.button_h) * iterator, width=self.button_w, height=self.button_h)

            # if cast_response.status_code == 200:
            #     cast = cast_response.json()
            #     self.actor_data.clear()
            #     self.clear_frame(self.actor_frame)

            #     for actor in cast:
            #         actor_name = actor['person']['name']
            #         character_name = actor['character']['name']

            #         if actor_name not in self.actor_data:
            #             self.actor_data[actor_name] = []
            #         self.actor_data[actor_name].append(character_name)

            #     for actor_name in self.actor_data:
            #         iterator = 1
            #         actor_size = len(self.actor_data)
            #         button = tk.Button(self.actor_frame, text=actor_name, command=lambda a=actor_name: self.show_roles(a), width=self.button_w, height=self.button_h)
            #         button.place(x=int(self.window_size / 2), y=100 + (actor_size / iterator))

    def show_roles(self, actor_name):
        self.clear_frame(self.results_frame)
        roles = self.actor_data[actor_name]
        role_text = f"Roles for {actor_name}:\n" + "\n".join(roles)
        label = tk.Label(self.results_frame, text=role_text, justify="left")
        label.pack()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TVMazeApp(root)
    root.mainloop()