import tkinter as tk
import requests
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from datetime import datetime
import io

def get_weather():
    city = city_entry.get()  # Get the city from the entry field
    if city:  # Check if a city name is provided
        # Make a GET request to the OpenWeatherMap API (replace 'your_api_key' with your actual API key)
        response_current = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=6ae2f71d7704cfd1dbd8f08d54e3e15e&units=metric')
        response_forecast = requests.get(f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid=6ae2f71d7704cfd1dbd8f08d54e3e15e&units=metric')
        
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
                        forecast_lbls[i]['text'] = f"{datetime.fromtimestamp(weather_forecast['list'][i*8]['dt']).strftime('%Y-%m-%d')}: {weather_forecast['list'][i*8]['main']['temp']}°C, {weather_forecast['list'][i*8]['weather'][0]['description']}"

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

def load_current_icon(url):
    response = requests.get(url, stream=True)
    img_data = response.content
    img = Image.open(io.BytesIO(img_data))
    img = img.resize((50, 50))
    current_icon = ImageTk.PhotoImage(img)
    current_icon_label.configure(image=current_icon)
    current_icon_label.image = current_icon

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
        dates.append(datetime.fromtimestamp(weather_forecast['list'][i*8]['dt']).strftime('%Y-%m-%d'))
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
    window.destroy()  # Close the window upon saving preferences

# Create the main window
window = tk.Tk()
window.title("Weather App")

# Set background image
background_image = Image.open("pexels-johannes-plenio-1118873.jpg")  # Replace with your image path
background_image = background_image.resize((800, 600), Image.BILINEAR)  # Example: Using BILINEAR resampling filter
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(window, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create the entry field and search button
city_entry = tk.Entry(window, font=("Helvetica", 12))
city_entry.pack(padx=10, pady=5)
search_button = tk.Button(window, text="Search Weather", command=get_weather, font=("Helvetica", 12))
search_button.pack(pady=5)

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