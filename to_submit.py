import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tkb
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import webbrowser

# Function to change units
def convert_temperature(value, from_unit, to_unit):
    if from_unit == "Celsius" and to_unit == "Fahrenheit":
        return (value * 9/5) + 32
    elif from_unit == "Fahrenheit" and to_unit == "Celsius":
        return (value - 32) * 5/9
    else:
        return value

# Function to fetch weather data for a city (replace this with your weather fetching logic)
def display_selected_day(date):
    selected_day_info = next((item for item in weather_data['list'] if item['dt_txt'].startswith(date)), None)
    if selected_day_info:
        temperature = selected_day_info['main']['temp']
        description = selected_day_info['weather'][0]['description']
        selected_day_text.delete(1.0, tk.END)
        selected_day_text.insert(tk.END, f"Selected Day: {date}\n")
        selected_day_text.insert(tk.END, f"Temperature: {temperature}°C\n")
        selected_day_text.insert(tk.END, f"Description: {description.capitalize()}\n")        

# Function to fetch weather data for a city (replace this with your weather fetching logic)
def display_weather_data():
    global weather_data
    global canvas
    city = city_entry.get()
    api_key = "6ae2f71d7704cfd1dbd8f08d54e3e15e"  # Replace with your API key
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        
    try:
        response = requests.get(url)
        weather_data = response.json()
        city_name = weather_data['city']['name']
        lat = weather_data['city']['coord']['lat']
        lon = weather_data['city']['coord']['lon']
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
        aqi_response = requests.get(aqi_url)
        aqi_data = aqi_response.json()
        uv_index_url = f'http://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid=3a951967f8e78b845a889f74e243577c'
        uv_response = requests.get(uv_index_url)
        uv_data = uv_response.json()
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city_name)
        if location:
            map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}"
            webbrowser.open_new(map_url)
        else:
            weather_text.insert(tk.END, f"Map for {city_name} is not available.\n")                       
        # Clear previous weather info and graph
        weather_text.delete(1.0, tk.END)
        selected_day_text.delete(1.0, tk.END)
        if 'canvas' in globals():
            canvas.get_tk_widget().destroy()

        # Display weather forecast for the current day
        current_date = datetime.strptime(weather_data['list'][0]['dt_txt'], "%Y-%m-%d %H:%M:%S").date()
        weather_text.insert(tk.END, f"Weather Forecast for {city}:\n")
        
        for item in weather_data['list']:
            item_date = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S").date()
            if item_date == current_date:
                temperature = item['main']['temp']
                description = item['weather'][0]['description']
                mintemp = item['main']['temp_min']
                maxtemp = item['main']['temp_max']
                humidity = item['main']['humidity']
                pressure = item['main']['pressure']
                windspeed = item['wind']['speed']
                weather_text.insert(tk.END, f"Current Temperature: {temperature}°C\n")
                weather_text.insert(tk.END, f"Description: {description.capitalize()}\n")
                weather_text.insert(tk.END, f"Minimum Temperature: {mintemp}°C\n")
                weather_text.insert(tk.END, f"Maximum Temperature: {maxtemp}°C\n")
                weather_text.insert(tk.END, f"Humidity: {humidity}\n")
                weather_text.insert(tk.END, f"Pressure: {pressure} hPa\n")
                weather_text.insert(tk.END, f"Wind Speed: {windspeed} m/s\n")
                break
            else:
                break
        
        for item in aqi_data['list']:
            aqindex = item['main']['aqi']
            weather_text.insert(tk.END, f"AQI: {aqindex}\n")
            break

        for item in uv_data:
            uv_index = uv_data['value']
            weather_text.insert(tk.END, f"UV Index: {uv_index}")
            break

        # Plotting the graph for the current day's temperature
        temperatures = [item['main']['temp'] for item in weather_data['list']]
        plt.figure(figsize=(5, 3))
        plt.plot(temperatures, marker='o', linestyle='-')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.title('Temperature Forecast for Next Hours')
        plt.tight_layout()

        # Display the graph on the Tkinter window
        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")

        # Display the next 5 days' weather as buttons
        next_dates = [current_date + timedelta(days=i) for i in range(1, 6)]
        for i, date in enumerate(next_dates):
            date_str = date.strftime("%Y-%m-%d")
            button = ttk.Button(window, text=date_str, command=lambda d=date_str: display_selected_day(d))
            button.place(relx=0.275 + i * 0.1, rely=0.85)

    except requests.RequestException as e:
        weather_text.insert(tk.END, f"Error: {e}")

# Create the Tkinter window
window = tkb.Window(themename="morph")
window.title("Weather Forecast")
window.geometry("1280x960")

# City entry
city_entry = tk.Entry(window)
city_entry.place(relx=0.5, y=20, anchor="n")

# Fetch weather button
fetch_button = tk.Button(window, text="Fetch Weather", command=display_weather_data)
fetch_button.place(relx=0.5, y=50, anchor="n")

# Weather text display
weather_text = tk.Text(window, height=10, width=50)
weather_text.place(relx=0.5, rely=0.2, anchor="center")
weather_text.config(font=("Helvetica", 12))

# Selected day weather text display
selected_day_text = tk.Text(window, height=4, width=40)
selected_day_text.place(relx=0.65, rely=0.75, anchor="e")
selected_day_text.config(font=("Helvetica", 12))

# Canvas initialization
canvas = FigureCanvasTkAgg(plt.figure(figsize=(5, 3)), master=window)

# Run the main loop
window.mainloop()
