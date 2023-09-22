import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageTk
import io

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("900x600")
        self.resizable(0, 0)
        self.dark_mode = tk.BooleanVar()
        self.dark_mode.set(False)

        self.weather_icons={}
        self.load_weather_icons()

        self.weather_history=[]

        self.units=tk.StringVar()
        self.units.set("metric")

        self.create_widgets()

    def create_widgets(self):
        self.configure_bg_color()

        # Search Entry
        self.search_label = ttk.Label(self, text="Enter Location:", font=("Poppins", 20), foreground="white", background="#404040")
        self.search_label.place(x=20, y=20)

        self.search_entry = ttk.Entry(self, justify='center', font=('poppins', 25, 'bold'), background='#404040', border=0, foreground='white')
        self.search_entry.place(x=220, y=20)
        self.search_entry.bind("<Return>", self.get_weather)
        self.search_entry.focus()

        # Search Button
        self.search_button = ttk.Button(self, text="Search", command=self.get_weather)
        self.search_button.place(x=620, y=14)

        # Unit Selection
        self.unit_label = ttk.Label(self, text="Select Units:", font=("Poppins", 20), foreground="white", background="#404040")
        self.unit_label.place(x=750, y=20)

        self.metric_radio=ttk.Radiobutton(self, text="Metric", variable=self.units, value="metric", command=self.get_weather)
        self.metric_radio.place(x=880, y=14)

        self.imperial_radio=ttk.Radiobutton(self, text="Imperial", variable=self.units, value="imperial", command=self.get_weather)
        self.imperial_radio.place(x=880, y=50)

        # Dark Mode Toggle
        self.dark_mode_label=ttk.Label(self, text="Dark Mode:", font=("Poppins", 20), foreground="white", background="#404040")
        self.dark_mode_label.place(x=750, y=100)

        self.dark_mode_checkbox=ttk.Checkbutton(self, variable=self.dark_mode, command=self.toggle_dark_mode)
        self.dark_mode_checkbox.place(x=880, y=94)

        # Current Weather Display
        self.current_weather_label=ttk.Label(self, text="Current Weather", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.current_weather_label.place(x=20, y=100)

        self.weather_icon=ttk.Label(self)
        self.weather_icon.place(x=30, y=140)

        self.temperature_label=ttk.Label(self, text="Temperature:", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.temperature_label.place(x=200, y=140)

        self.description_label=ttk.Label(self, text="Description:", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.description_label.place(x=200, y=180)

        self.wind_label=ttk.Label(self, text="Wind:", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.wind_label.place(x=200, y=220)

        self.humidity_label=ttk.Label(self, text="Humidity:", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.humidity_label.place(x=200, y=260)

        self.pressure_label=ttk.Label(self, text="Pressure:", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.pressure_label.place(x=200, y=300)

        self.time_label=ttk.Label(self, text="Local Time:", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.time_label.place(x=600, y=100)

        self.time_display=ttk.Label(self, text="", font=("Helvetica", 20))
        self.time_display.place(x=600, y=140)

        # Forecast Treeview
        self.forecast_label=ttk.Label(self, text="5-Day Forecast", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.forecast_label.place(x=600, y=250)

        self.forecast_tree=ttk.Treeview(self, columns=("Day", "Min Temp", "Max Temp"), show="headings")
        self.forecast_tree.heading("Day", text="Day")
        self.forecast_tree.heading("Min Temp", text="Min Temp (°C)")
        self.forecast_tree.heading("Max Temp", text="Max Temp (°C)")
        self.forecast_tree.column("Day", width=150)
        self.forecast_tree.column("Min Temp", width=100)
        self.forecast_tree.column("Max Temp", width=100)
        self.forecast_tree.place(x=600, y=290)

        # Weather History Treeview
        self.history_label=ttk.Label(self, text="7-Day Weather History", font=("Arial", 15, "bold"), foreground="white", background="#404040")
        self.history_label.place(x=600, y=450)

        self.history_tree=ttk.Treeview(self, columns=("Date", "Description", "Min Temp", "Max Temp"), show="headings")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Description", text="Description")
        self.history_tree.heading("Min Temp", text="Min Temp (°C)")
        self.history_tree.heading("Max Temp", text="Max Temp (°C)")
        self.history_tree.column("Date", width=150)
        self.history_tree.column("Description", width=150)
        self.history_tree.column("Min Temp", width=100)
        self.history_tree.column("Max Temp", width=100)
        self.history_tree.place(x=600, y=490)

    def toggle_dark_mode(self):
        self.configure_bg_color()

    def configure_bg_color(self):
        bg_color= "#404040"if self.dark_mode.get()else"white"
        fg_color="white"if self.dark_mode.get()else"black"
        self.configure(background=bg_color)

        self.search_label.configure(background=bg_color,foreground=fg_color)
        self.search_entry.configure(background=bg_color,foreground=fg_color)
        self.search_button.configure(background=bg_color,foreground=fg_color)

        self.unit_label.configure(background=bg_color,foreground=fg_color)
        self.metric_radio.configure(background=bg_color,foreground=fg_color, selectcolor=bg_color)
        self.imperial_radio.configure(background=bg_color,foreground=fg_color, selectcolor=bg_color)

        self.dark_mode_label.configure(background=bg_color,foreground=fg_color)
        self.dark_mode_checkbox.configure(background=bg_color,foreground=fg_color, selectcolor=bg_color)

        self.current_weather_label.configure(background=bg_color,foreground=fg_color)

        self.temperature_label.configure(background=bg_color,foreground=fg_color)
        self.description_label.configure(background=bg_color,foreground=fg_color)
        self.wind_label.configure(background=bg_color,foreground=fg_color)
        self.humidity_label.configure(background=bg_color,foreground=fg_color)
        self.pressure_label.configure(background=bg_color,foreground=fg_color)

        self.time_label.configure(background=bg_color,foreground=fg_color)
        self.time_display.configure(background=bg_color,foreground=fg_color)

        self.forecast_label.configure(background=bg_color,foreground=fg_color)
        self.forecast_tree.configure(background=bg_color,foreground=fg_color)

        self.history_label.configure(background=bg_color,foreground=fg_color)
        self.history_tree.configure(background=bg_color,foreground=fg_color)

    def load_weather_icons(self):
        icon_ids = ["01d", 01n","02d","02n","03d","03n","04d","04n","09d","09n","10d","10n","11d", "11n", "13d","13n","50d","50n"]
        for icon_id in icon_ids:
            icon_url=f"http://openweathermap.org/img/w/{icon_id}.png"
            icon_data=requests.get(icon_url, stream=True).content
            icon=Image.open(io.BytesIO(icon_data))
            icon=ImageTk.PhotoImage(icon)
            self.weather_icons[icon_id] = icon

    def get_weather(self, event=None):
        try:
            location=self.search_entry.get()
            units=self.units.get()

            if location:
                self.search_entry.delete(0, tk.END)

                # Geocode the location
                geolocator=Nominatim(user_agent="geoapiExercises")
                location_info=geolocator.geocode(location, timeout=None)  # No timeout for geocoding
                if location_info:
                    lat, lon=location_info.latitude,location_info.longitude

                    # Fetch current weather data
                    current_weather=self.get_current_weather(lat, lon, units)
                    if current_weather:
                        # Displaycurrentweatherdata
                        self.display_current_weather(current_weather)

                        # Fetch5-dayforecastdata
                        forecast_data=self.get_5_day_forecast(lat, lon, units)
                        if forecast_data:
                            # Display5-dayforecast data
                            self.display_5_day_forecast(forecast_data)

                        # Fetc 7-dayweatherhistorydata
                        history_data=self.get_7_day_weather_history(lat, lon, units)
                        if history_data:
                            # Display7-dayweatherhistory data
                            self.display_7_day_weather_history(history_data)

                        # Addthelocationtothehistorylist
                        self.add_to_history(location)

                    else:
                        messagebox.showerror('Weather App', 'Unable to fetch weather data.')

                else:
                    messagebox.showerror('Weather App', 'Location not found.')

        except GeocoderTimedOut:
            messagebox.showerror('Weather App', 'Geocoding request timed out. Try again.')

        except Exception as e:
            messagebox.showerror('Weather App', f'Error: {str(e)}')

    def get_current_weather(self, lat, lon, units):
        try:
            api_key = 'YOUR_OPENWEATHERMAP_API_KEY'
            api = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={api_key}'
            json_data = requests.get(api).json()

            if 'weather' in json_data and 'main' in json_data and 'wind' in json_data and 'dt' in json_data:
                return json_data

        except Exception as e:
            print(e)

        return None

    def display_current_weather(self, weather_data):
        # Display current weather data in the GUI
        condition=weather_data['weather'][0]['main']
        description=weather_data['weather'][0]['description']
        temp=weather_data['main']['temp']
        pressure=weather_data['main']['pressure']
        humidity=weather_data['main']['humidity']
        wind=weather_data['wind']['speed']

        self.temperature_label.config(text=f"Temperature: {temp}°C" if self.units.get()=="metric" else f"Temperature: {temp}°F")
        self.description_label.config(text=f"Description: {description}")
        self.wind_label.config(text=f"Wind: {wind} m/s")
        self.humidity_label.config(text=f"Humidity: {humidity}%")
        self.pressure_label.config(text=f"Pressure: {pressure} hPa")

        # Weather Icon
        weather_icon_id=weather_data['weather'][0]['icon']
        self.load_weather_icon(weather_icon_id)

        # Local Time
        timestamp=weather_data['dt']
        local_time=datetime.utcfromtimestamp(timestamp).strftime("%I:%M %p")
        self.time_display.config(text=local_time)

    def get_5_day_forecast(self, lat, lon, units):
        try:
            api_key= 'YOUR_OPENWEATHERMAP_API_KEY'
            api=f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units={units}&appid={api_key}'
            json_data=requests.get(api).json()

            if 'list' in json_data:
                return json_data['list']

        except Exception as e:
            print(e)

        return None

    def display_5_day_forecast(self, forecast_data):
        # Display 5-day forecast data in the GUI
        self.forecast_tree.delete(*self.forecast_tree.get_children())

        for entry in forecast_data:
            timestamp = entry['dt']
            day = datetime.utcfromtimestamp(timestamp).strftime("%A")
            min_temp=entry['main']['temp_min']
            max_temp=entry['main']['temp_max']
            min_temp_str=f"{min_temp}°C" if self.units.get() == "metric" else f"{min_temp}°F"
            max_temp_str=f"{max_temp}°C" if self.units.get() == "metric" else f"{max_temp}°F"

            self.forecast_tree.insert("", "end", values=(day, min_temp_str, max_temp_str))

    def get_7_day_weather_history(self, lat, lon, units):
        try:
            api_key = 'YOUR_OPENWEATHERMAP_API_KEY'
            # Set the start date for the history (7 days ago)
            start_date=datetime.now() - timedelta(days=7)
            start_timestamp=int(start_date.timestamp())
            api = f'https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&units={units}&dt={start_timestamp}&appid={api_key}'
            json_data=requests.get(api).json()

            if 'hourly' in json_data:
                return json_data['hourly']

        except Exception as e:
            print(e)

        return None

    def display_7_day_weather_history(self, history_data):
        # Display 7-day weather history data in the GUI
        self.history_tree.delete(*self.history_tree.get_children())

        for entry in history_data:
            timestamp=entry['dt']
            date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            description=entry['weather'][0]['description']
            min_temp=entry['main']['temp']
            max_temp=min_temp  # Since history data doesn't include max temp
            min_temp_str=f"{min_temp}°C" if self.units.get() == "metric" else f"{min_temp}°F"
            max_temp_str=f"{max_temp}°C" if self.units.get() == "metric" else f"{max_temp}°F"

            self.history_tree.insert("", "end", values=(date, description, min_temp_str, max_temp_str))

    def add_to_history(self, location):
        if location not in self.weather_history:
            self.weather_history.append(location)
            self.history_listbox.insert(tk.END, location)

    def load_weather_icon(self, icon_id):
        if icon_id in self.weather_icons:
            icon=self.weather_icons[icon_id]
            self.weather_icon.config(image=icon)
            self.weather_icon.image = icon

if __name__ == "__main__":
    app =WeatherApp()
    app.mainloop()
