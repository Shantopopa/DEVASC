import tkinter as tk
from tkinter import ttk, messagebox
import requests
import urllib.parse
from tkintermapview import TkinterMapView
from fpdf import FPDF
from googletrans import Translator

class GeoLocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.root.title("TrailBlazer")

        self.bg_color = "#f0f0f0"  # Light grey background
        self.fg_color = "#333333"  # Dark grey for text
        self.button_color = "#4CAF50"  # Green for buttons
        self.highlight_color = "#ffffff"  # White for highlight

        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.grid(padx=10, pady=10)

        self.translator = Translator()

        # Language selection for translation
        self.language_code_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt"
        }

        # API Key
        self.key = "9380c078-a7ca-4a9b-8f0b-45021d1f03e4"  # Replace with your Graphhopper API key
        self.route_url = "https://graphhopper.com/api/1/route?"

        # Create input fields and map
        self.create_widgets()
        self.create_map()  # Call to create the map
        self.markers = []  # List to hold the markers

    def create_widgets(self):

        # Create a frame for better organization with a background color
        border_frame = tk.Frame(self.root, bg="black", bd=2, relief="solid")  # Border frame
        border_frame.grid(padx=10, pady=10)

        # Create a frame for better organization with a background color
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.grid(padx=10, pady=10)

        # Starting Location
        tk.Label(frame, text="Starting Location:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky='e', padx=(0, 10), pady=(5, 5))
        self.start_loc = tk.Entry(frame, width=30)
        self.start_loc.grid(row=0, column=1, padx=(0, 20), pady=(5, 5), sticky='ew')

        # Destination Location
        tk.Label(frame, text="Destination Location:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=(5, 5))
        self.dest_loc = tk.Entry(frame, width=30)
        self.dest_loc.grid(row=1, column=1, padx=(0, 20), pady=(5, 5), sticky='ew')

        # Vehicle Profile
        tk.Label(frame, text="Vehicle Profile:", bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, sticky='e', padx=(0, 10), pady=(5, 5))
        self.vehicle_profile = ttk.Combobox(frame, values=["car", "bike", "foot"], width=28)
        self.vehicle_profile.grid(row=2, column=1, padx=(0, 20), pady=(5, 5), sticky='ew')
        self.vehicle_profile.current(0)  # Default to car

        # Distance Unit
        tk.Label(frame, text="Distance Unit:", bg=self.bg_color, fg=self.fg_color).grid(row=3, column=0, sticky='e', padx=(0, 10), pady=(5, 5))
        self.distance_unit = tk.StringVar(value="Kilometers")  # Default to Kilometers
        distance_units = ["Kilometers", "Miles", "Meters", "Feet", "Nautical Miles", "Yards"]
        self.distance_unit_combobox = ttk.Combobox(frame, values=distance_units, width=28, textvariable=self.distance_unit)
        self.distance_unit_combobox.grid(row=3, column=1, padx=(0, 20), pady=(5, 5), sticky='ew')
        self.distance_unit_combobox.current(0)  # Default to Kilometers

        # Translation
        tk.Label(frame, text="Translate to:", bg=self.bg_color, fg=self.fg_color).grid(row=4, column=0, sticky='e', padx=(0, 10), pady=(5, 5))
        self.language_var = tk.StringVar(value="en")  # Default to English
        languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese"]  # Example languages
        self.language_combobox = ttk.Combobox(frame, values=languages, width=28, textvariable=self.language_var)
        self.language_combobox.grid(row=4, column=1, padx=(0, 20), pady=(5, 5), sticky='ew')
        self.language_combobox.current(0)  # Default to English

        # Submit Button
        submit_button = tk.Button(frame, text="GET DIRECTIONS", command=self.get_directions, bg=self.button_color, fg=self.highlight_color)
        submit_button.grid(row=5, column=1, pady=(10, 5), sticky="ew")

        # Clear Button
        clear_button = tk.Button(frame, text="CLEAR", command=self.clear_inputs, bg=self.button_color, fg=self.highlight_color)
        clear_button.grid(row=6, column=1, pady=(10, 5), sticky="ew")

        # Export to PDF Button
        export_button = tk.Button(frame, text="EXPORT TO PDF", command=self.export_to_pdf, bg=self.button_color, fg=self.highlight_color)
        export_button.grid(row=7, column=1, pady=(10, 5), sticky="ew")

        # Configure the grid columns to expand evenly
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        # Output Area for Instructions
        self.output_area = ttk.Treeview(frame, columns=("Description", "Distance"), show='headings', height=10)
        self.output_area.heading("Description", text="Description")
        self.output_area.heading("Distance", text="Distance")
        self.output_area.column("Description", width=400)  # Set width for Description column
        self.output_area.column("Distance", width=150)  # Set width for Distance column
        self.output_area.grid(row=8, columnspan=2, pady=(10, 5), padx=(0, 20), sticky='ew')

        # Output Area for Distance and Trip Duration
        tk.Label(frame, text="Distance & Duration:", bg=self.bg_color, fg=self.fg_color).grid(row=9, column=0, columnspan=2, pady=(10, 0))
        self.distance_output_area = ttk.Treeview(frame, columns=("Output"), show='headings', height=5)
        self.distance_output_area.heading("Output", text="Output")
        self.distance_output_area.column("Output", width=400)  # Set width for Output column
        self.distance_output_area.grid(row=10, columnspan=2, pady=(10, 5), padx=(0, 20), sticky='ew')

    def clear_inputs(self):
        """Clear all input fields and output areas."""
        self.start_loc.delete(0, tk.END)
        self.dest_loc.delete(0, tk.END)
        self.vehicle_profile.set("car")  # Reset to default value
        self.distance_unit.set("Kilometers")  # Reset to default value
        
        # Clear output areas
        self.output_area.delete(*self.output_area.get_children())
        self.distance_output_area.delete(*self.distance_output_area.get_children())

        # Clear map markers if needed
        self.clear_markers()


    def create_map(self):
        # Create the map
        self.map = TkinterMapView(self.root, width=700, height=600, highlightthickness=2, bd=5, bg="black")
        self.map.grid(row=0, column=2, rowspan=8, padx=(10, 12))  # Adjust position to be on the right side
        self.map.set_position(0, 0)  # Set initial map position to center
        self.map.set_zoom(2)  # Set initial zoom level

    def clear_markers(self):
        """Clear all markers from the map."""
        for marker in self.markers:
            marker.delete()  # Delete each marker from the map
        self.markers.clear()  # Clear the list of markers

    def add_marker(self, lat, lng, label):
        """Add a marker to the map."""
        marker = self.map.set_marker(lat, lng, text=label)  # Add marker to map
        self.markers.append(marker)  # Save the marker to the list

    def geocoding(self, location):
        geocode_url = "https://graphhopper.com/api/1/geocode?"
        url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": self.key})

        replydata = requests.get(url)
        json_data = replydata.json()
        json_status = replydata.status_code

        if json_status == 200 and len(json_data["hits"]) != 0:
            lat = json_data["hits"][0]["point"]["lat"]
            lng = json_data["hits"][0]["point"]["lng"]
            name = json_data["hits"][0]["name"]
            value = json_data["hits"][0]["osm_value"]
            country = json_data["hits"][0].get("country", "")
            state = json_data["hits"][0].get("state", "")
            
            new_loc = f"{name}, {state}, {country}" if state and country else f"{name}, {country}" if country else name
            return json_status, lat, lng, new_loc, value
        else:
            return json_status, None, None, location, None
    
    def translate_text(self, text):
        """Translate the text to the selected language."""
        translated = self.translator.translate(text, dest=self.language_var.get())
        return translated.text

    def get_directions(self):
        start = self.start_loc.get()
        destination = self.dest_loc.get()
        vehicle = self.vehicle_profile.get()

        orig = self.geocoding(start)
        dest = self.geocoding(destination)

        if orig[0] == 200 and dest[0] == 200:
            # Fetch route and instructions
            paths_url = self.route_url + urllib.parse.urlencode({"key": self.key, "vehicle": vehicle}) + f"&point={orig[1]},{orig[2]}" + f"&point={dest[1]},{dest[2]}"
            paths_data = requests.get(paths_url).json()

            if paths_data["paths"]:
                distance_km = paths_data["paths"][0]["distance"] / 1000
                time_sec = int(paths_data["paths"][0]["time"] / 1000)
                    
                # Clear output areas
                self.output_area.delete(*self.output_area.get_children())
                self.distance_output_area.delete(*self.distance_output_area.get_children())

                # Translate and add distance and duration output
                distance_text = f"Driving Distance: {distance_km:.1f} km"
                self.distance_output_area.insert('', 'end', values=(self.translate_text(distance_text),))
                time_text = f"Trip Duration: {time_sec//3600:02d}:{(time_sec%3600)//60:02d}:{time_sec%60:02d}"
                self.distance_output_area.insert('', 'end', values=(self.translate_text(time_text),))

                # Translate and display instructions
                for instruction in paths_data["paths"][0]["instructions"]:
                    path_desc = self.translate_text(instruction["text"])  # Translate instruction text
                    path_distance = instruction["distance"] / 1000  # Convert to kilometers
                    self.output_area.insert('', 'end', values=(path_desc, f"{path_distance:.1f} km"))  # Add distance next to instruction
                    
                # Calculate average speed
                average_speed_kmh = distance_km / (time_sec / 3600)
                average_speed_mph = average_speed_kmh / 1.60934
                self.output_area.insert('', 'end', values=(f"Average Speed: {average_speed_kmh:.1f} km/h / {average_speed_mph:.1f} mph",))

                 # Add markers for the start and destination locations
                self.add_marker(orig[1], orig[2], "Start")  # Add marker for starting location
                self.add_marker(dest[1], dest[2], "Destination")  # Add marker for destination location

                # Center the map on the midpoint between the origin and destination
                mid_lat = (orig[1] + dest[1]) / 2  # Calculate midpoint latitude
                mid_lng = (orig[2] + dest[2]) / 2  # Calculate midpoint longitude
                self.map.set_position(mid_lat, mid_lng)  # Center map at midpoint
                self.map.set_zoom(10)  # Adjust zoom level (change this as needed)    
                
            else:
                 messagebox.showerror("Error", "No paths found. Please check your input locations.")
        else:
            messagebox.showerror("Error", "Could not geocode the locations. Please check the input.")

    def export_to_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.cell(200, 10, txt="Geolocation Finder Output", ln=True, align='C')

        pdf.ln(10)  # New line

        # Add starting and destination locations
        pdf.cell(200, 10, txt="Starting Location: " + self.start_loc.get(), ln=True)
        pdf.cell(200, 10, txt="Destination Location: " + self.dest_loc.get(), ln=True)
        pdf.cell(200, 10, txt="Vehicle Profile: " + self.vehicle_profile.get(), ln=True)
        pdf.ln(10)  # New line

        # Add instructions from the output area
        pdf.cell(200, 10, txt="Instructions:", ln=True)
        for item in self.output_area.get_children():
            values = self.output_area.item(item, 'values')  # Get all values
            if len(values) >= 2:  # Check if there are at least two values
                instruction = values[0]  # Get the instruction
                distance = values[1]  # Get the distance
                pdf.cell(200, 10, txt=f"{instruction} - {distance}", ln=True)

        pdf.ln(10)  # New line

        # Add distances from the distance output area
        pdf.cell(200, 10, txt="Distance & Duration:", ln=True)
        for item in self.distance_output_area.get_children():
            output = self.distance_output_area.item(item, 'values')[0]  # Get only the first value
            pdf.cell(200, 10, txt=output, ln=True)

        # Save the PDF to a file
        pdf_file_path = r"C:\Users\user\Desktop\python folder\DEVASC\File Downloads\geolocation_output.pdf"
        pdf.output(pdf_file_path)
        messagebox.showinfo("Export to PDF", f"Output successfully exported to {pdf_file_path}")

if __name__ == "__main__":
    root = tk.Tk()

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set the window size, leaving space for the taskbar
    taskbar_height = 40  # Approximate height of the taskbar; adjust as needed
    root.geometry(f"{screen_width}x{screen_height - taskbar_height}+0+0")

    root.attributes('-fullscreen', False)  # Do not enable full screen mode
    app = GeoLocatorApp(root)
    root.mainloop()