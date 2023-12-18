import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tkb
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from tkinter import *
import tkinter.messagebox as MessageBox
import mysql.connector as mysql

current_unit = 'Celsius'
root=tkb.Window(themename="morph")
root.geometry("640x480")
root.title("Home")

# Function for Login
def Login():
    root = tkb.Window(themename="morph")
    root.geometry("640x480")
    root.title("Login")
    U = Label(root, text='Username')
    U.place(x=75, y=180)
    P = Label(root, text='Password') # type: ignore
    P.place(x=75, y=220)
    u_name = Entry(root, width=69)
    u_name.place(x=150, y=180)
    p_word = Entry(root, width=69)
    p_word.place(x=150, y=220)

    def w3():
        username = u_name.get()
        password = p_word.get()
        mycon = mysql.connect(host='localhost',
                              user='root',
                              password='hax@mysql',
                              database='minipy')
        mycur = mycon.cursor()
        mycur.execute('select * from data')
        a = mycur.fetchall()
        mycon.commit()
        for i in a:
            if i[1] == username and i[2] == password:
                MessageBox.showinfo('Verified')
                root.destroy()

                def convert_temperature():
                    global weather_data
                    global current_unit
                
                    
                    if current_unit == 'Celsius':
                        for item in weather_data['list']:
                            item['main']['temp'] = (item['main']['temp'] * 9/5) + 32
                            item['main']['temp_min'] = (item['main']['temp_min'] * 9/5) + 32
                            item['main']['temp_max'] = (item['main']['temp_max'] * 9/5) + 32
                        current_unit = 'Fahrenheit'
                        convert_button.config(text="Switch to Celsius")
                    else:
                        for item in weather_data['list']:
                            item['main']['temp'] = (item['main']['temp'] - 32) * 5/9
                            item['main']['temp_min'] = (item['main']['temp_min'] - 32) * 5/9
                            item['main']['temp_max'] = (item['main']['temp_max'] - 32) * 5/9
                        current_unit = 'Celsius'
                        convert_button.config(text="Switch to Fahrenheit")
                    
                    display_weather_data()

                def display_selected_day(date):
                    selected_day_info = next((item for item in weather_data['list'] if item['dt_txt'].startswith(date)), None)
                    if selected_day_info:
                        temperature = selected_day_info['main']['temp']
                        description = selected_day_info['weather'][0]['description']
                        selected_date = datetime.strptime(date, "%Y-%m-%d")
                        selected_day_text.delete(1.0, tk.END)
                        selected_day_text.insert(tk.END, f"Selected Day: {selected_date}\n")
                        selected_day_text.insert(tk.END, f"Temperature: {temperature:.2f}°{current_unit}\n")
                        selected_day_text.insert(tk.END, f"Description: {description.capitalize()}\n")

                def display_weather_data():
                    global weather_data
                    global canvas
                    global current_unit
                    
                    city = city_entry.get()
                    api_key = "3a951967f8e78b845a889f74e243577c" # Replace with your API key
                    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
                    
                    try:
                        response = requests.get(url)
                        weather_data = response.json()
                        current_weather_condition = weather_data['list'][0]['weather'][0]['main'].lower()
                        if 'rain' in current_weather_condition:
                            window.configure(bg='dark blue')  # You can change 'blue' to the desired color
                        elif 'cloud' in current_weather_condition:
                            window.configure(bg='gray')  # You can change 'gray' to the desired color
                        elif 'clear' in current_weather_condition:
                            window.configure(bg='yellow')  # You can change 'yellow' to the desired color
                        else:
                            window.configure(bg='white')
                        
                        lat = weather_data['city']['coord']['lat']
                        lon = weather_data['city']['coord']['lon']
                        
                        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
                        aqi_response = requests.get(aqi_url)
                        aqi_data = aqi_response.json()
                        
                        uv_index_url = f'http://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid=3a951967f8e78b845a889f74e243577c'
                        uv_response = requests.get(uv_index_url)
                        uv_data = uv_response.json()
                        
                        # Clear previous weather info and graph
                        weather_text.delete(1.0, tk.END)
                        selected_day_text.delete(1.0, tk.END)
                        if 'canvas' in globals():
                            canvas.get_tk_widget().destroy() # type: ignore
                        
                        # Display weather forecast
                        weather_text.insert(tk.END, f"Weather Forecast for {city}:")
                        temperatures = []
                        for i in range(0, 6):
                            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                            weather_text.insert(tk.END, f"\nWeather for {date}:\n")
                            for item in weather_data['list']:
                                item_date = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S").date()
                                if item_date == datetime.now().date() + timedelta(days=i):
                                    temperature = item['main']['temp']
                                    mintemp = item['main']['temp_min']
                                    maxtemp = item['main']['temp_max']
                                    if current_unit == 'Fahrenheit':
                                        temperature = (temperature * 9/5) + 32
                                        mintemp = (mintemp * 9/5) + 32
                                        maxtemp = (maxtemp * 9/5) + 32
                                    temperatures.append(temperature)
                                    description = item['weather'][0]['description']
                                    humidity = item['main']['humidity']
                                    pressure = item['main']['pressure']
                                    windspeed = item['wind']['speed']
                                    weather_text.insert(tk.END, f"Current Temperature: {temperature:.2f}°{current_unit}\n")
                                    weather_text.insert(tk.END, f"Minimum Temperature: {mintemp:.2f}°{current_unit}\n")
                                    weather_text.insert(tk.END, f"Maximum Temperature: {maxtemp:.2f}°{current_unit}\n")
                                    weather_text.insert(tk.END, f"Description: {description.capitalize()}\n")
                                    weather_text.insert(tk.END, f"Humidity: {humidity}\n")
                                    weather_text.insert(tk.END, f"Pressure: {pressure} hPa\n")
                                    weather_text.insert(tk.END, f"Wind Speed: {windspeed} m/s\n")
                                    for item in uv_data:
                                        uv_index = uv_data['value']
                                        weather_text.insert(tk.END, f"UV Index: {uv_index}\n")
                                        break
                                    for item in aqi_data['list']:
                                        aqindex = item['main']['aqi']
                                        weather_text.insert(tk.END, f"AQI: {aqindex}\n")
                                        break
                                    else:
                                        weather_text.insert(tk.END, "AQI data not available\n")
                                    break
                        
                        # Plotting the graph for the next 5 days' temperature
                        plt.figure(figsize=(5, 3))
                        plt.plot(temperatures, marker='o', linestyle='-')
                        plt.xlabel('Time')
                        plt.ylabel(f'Temperature ({current_unit})')
                        plt.title(f'Temperature Forecast for the Next 5 Days')
                        plt.tight_layout()
                        
                        # Display the graph on the Tkinter window
                        fig = plt.gcf()
                        canvas = FigureCanvasTkAgg(fig, master=window)
                        canvas.draw()
                        canvas.get_tk_widget().place(relx=0.5, rely=0.52, anchor="center")
                        
                        # Display the next 5 days' weather as buttons
                        next_dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 6)]
                        for i, date in enumerate(next_dates):
                            button = ttk.Button(window, text=date, command=lambda d=date: display_selected_day(d))
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
                fetch_button = tkb.Button(window, text="Fetch Weather", command=display_weather_data, cursor="hand2")
                fetch_button.place(relx=0.5, y=50, anchor="n")

                current_unit = 'Celsius'  # Set initial temperature unit
                convert_button = tkb.Button(window, text="Switch to Fahrenheit", command=convert_temperature, cursor="hand2")
                convert_button.place(relx=0.5, y=310, anchor="n")

                # Weather text display
                weather_text = tk.Text(window, height=11, width=50)
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

####
                                
            else:
                MessageBox.showinfo('Wrong credentials')
                root.destroy()

    Verify1 = tkb.Button(root, text='Verify', command=w3, width=13, cursor="hand2")
    Verify1.place(x=100, y=250)
    
# Registration
def Registration():
    root = tkb.Window(themename="morph")
    root.title('Registration')
    root.geometry('640x480')
    EMLabel = Label(root, text='Email:')
    EMLabel.place(x=150, y=180)
    NLabel = Label(root, text='Name:')
    NLabel.place(x=150, y=210)
    PLabel = Label(root, text='Password:')
    PLabel.place(x=150, y=240)
    e = Entry(root, width=30, justify='center')
    e.place(x=230, y=180)
    f = Entry(root, width=30, justify='center')
    f.place(x=230, y=210)
    g = Entry(root, width=30, justify='center')
    g.place(x=230, y=240)

    def f1():
        email = e.get()
        name = f.get()
        passw = g.get()
        mycon = mysql.connect(host='localhost',
                              user='root',
                              password='hax@mysql',
                              database='minipy')
        mycur = mycon.cursor()
        mycur.execute('insert into data values(%s,%s,%s)',(email, name, passw))
        mycon.commit()
        MessageBox.showinfo('Registered sucessfully!')
        e.delete(0, 'end')
        f.delete(0, 'end')
        g.delete(0, 'end')
        root.destroy()

    myButton = tkb.Button(root, text='Register', command=f1, width=13, cursor="hand2").place(x=450, y=180)

# Main window buttons
Vbutton = tkb.Button(root, text='Login', command=Login, width=13, cursor="hand2").place(x=150, y=180)
Cbutton = tkb.Button(root, text='Sign Up', command=Registration, width=13, cursor="hand2").place(x=400, y=180)


root.mainloop()
