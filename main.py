import tkinter as tk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tkb
import matplotlib.pyplot as plt
from datetime import datetime
import io


def get_weather():
    
    city = city_entry.get()  # Get the city from the entry field
    api_key = "API_KEY"
    if city: # Check if a city name is provided
        # Make a GET request to the OpenWeatherMap API (replace 'API_KEY' with your actual API key)
        response_current = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
        response_forecast = requests.get(f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric')
        
        # Check if the API request was successful (status code 200)
        if response_current.status_code == 200 and response_forecast.status_code == 200:
            try:
                weather_current = response_current.json()
                weather_forecast = response_forecast.json()

                # Check if 'main' key exists in weather_current data
                if 'main' in weather_current and 'weather' in weather_current:
                    # Update the labels with the weather data
                    current_lbl['text'] = f"Current: {weather_current['main']['temp']}°C, {weather_current['weather'][0]['description']}" 

                    # Display weather icons
                    current_icon_url = f"http://openweathermap.org/img/w/{weather_current['weather'][0]['icon']}.png"
                    load_current_icon(current_icon_url)

                    for i in range(5):
                        forecast_lbls[i]['text'] = f"{datetime.fromtimestamp(weather_forecast['list'][i*8]['dt']).strftime('%d-%m-%Y')}: {weather_forecast['list'][i*8]['main']['temp']}°C, {weather_forecast['list'][i*8]['weather'][0]['description']}" #type:ignore

                        # Display weather icons for forecast
                        forecast_icon_url = f"http://openweathermap.org/img/w/{weather_forecast['list'][i*8]['weather'][0]['icon']}.png"
                        load_forecast_icon(forecast_icon_url, i)

                    # Create a simple temperature graph
                    create_temperature_graph(weather_forecast)
                else:
                    current_lbl['text'] = "Weather data not available" 
            except KeyError as e:
                current_lbl['text'] = f"Error: {e}" 
        else:
            current_lbl['text'] = "Failed to fetch weather data"
    else:
        current_lbl['text'] = "Please enter a city name"
def search():
    city=city_entry.get()
    result=get_weather()
    if result is None:
        return
    icon_url, temperature, description, city, country = result #type:ignore
    location_label.configure(text=f"{city}, {country}")

    image=Image.open(requests.get(icon_url, stream=True).raw)
    icon=ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image=icon  # type: ignore

    temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
    description_label.configure(text=f"Description: {description}")

def load_current_icon(url):
    response = requests.get(url, stream=True)
    img_data = response.content
    img = Image.open(io.BytesIO(img_data))
    img = img.resize((50, 50))
    current_icon = ImageTk.PhotoImage(img)
    current_icon_label.configure(image=current_icon)
    current_icon_label.image = current_icon  # type: ignore

def load_forecast_icon(url, index):
    response = requests.get(url, stream=True)
    img_data = response.content
    img = Image.open(io.BytesIO(img_data))
    img = img.resize((30, 30))
    forecast_icon = ImageTk.PhotoImage(img)
    forecast_icon_labels[index].configure(image=forecast_icon)
    forecast_icon_labels[index].image = forecast_icon

def create_temperature_graph(weather_forecast):
    dates = []
    temperatures = []
    for i in range(5):
        dates.append(datetime.fromtimestamp(weather_forecast['list'][i*8]['dt']).strftime('%d-%m-%Y'))
        temperatures.append(weather_forecast['list'][i*8]['main']['temp'])

    plt.figure(figsize=(8, 4))
    plt.plot(dates, temperatures, marker='o', linestyle='-', color='blue')
    plt.title('5-Day Temperature Forecast')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the graph
    plt.show()

def save_preferences():
    city = city_entry.get()
    with open('user_preferences.txt', 'w') as file:
        file.write(city)
    window.destroy() # Close the window upon saving preferences

# Create the main window
window=tkb.Window(themename="morph")
window.title("Weather App")
window.geometry("1280x720")

# Create the entry field and search button
city_entry=tkb.Entry(window, font="Helvetica, 18")
city_entry.pack(pady=10)
search_button=tkb.Button(window, text="Search", command=search, bootstyle="warning", cursor="hand2")  # type: ignore
search_button.pack(pady=10)

# Create the label for location
location_label=tk.Label(window, font="Helvetica, 25")
location_label.pack(pady=20)

# Create the label for weather icons
icon_label=tk.Label(window)
icon_label.pack()

# Create the label for temperature
temperature_label=tk.Label(window, font="Helvetica, 20")
temperature_label.pack()

# Create the label for weather description
description_label=tk.Label(window, font="Helvetica, 20")
description_label.pack()

# Create the label for the current weather
current_lbl = tk.Label(window, text="", font=("Helvetica", 16, "bold"))
current_lbl.pack()

current_icon_label = tk.Label(window)
current_icon_label.pack()

# Create the frames for forecast display
forecast_frame = tk.Frame(window)
forecast_frame.pack()

# Create the labels for the forecast with icons
forecast_lbls = [tk.Label(forecast_frame, text="", font=("Helvetica", 12)) for _ in range(5)]
forecast_icon_labels = [tk.Label(forecast_frame) for _ in range(5)]

for i in range(5):
    forecast_lbls[i].pack(anchor=tk.W)
    forecast_icon_labels[i].pack(anchor=tk.E)

# Save preferences when closing the window
window.protocol("WM_DELETE_WINDOW", save_preferences)

# Run the application
window.mainloop()
