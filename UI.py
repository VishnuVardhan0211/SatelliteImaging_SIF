import tkinter as tk
import speech_recognition as sr
import os
from keybert import KeyBERT
import requests
import folium
import webbrowser


stored_text = ""  # Variable to store recognized speech

def get_text():
    return text_entry.get()

def recognize_speech():
    global stored_text
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio_text.config(state=tk.NORMAL)
        audio_text.delete(1.0, tk.END)
        audio_text.insert(tk.END, "Listening... Speak now.")
        audio_text.config(state=tk.DISABLED)
        audio_text.update_idletasks()
        audio = r.listen(source)

    try:
        recognized_text = r.recognize_google(audio)
        audio_text.config(state=tk.NORMAL)
        audio_text.delete(1.0, tk.END)
        audio_text.insert(tk.END, recognized_text)
        audio_text.config(state=tk.DISABLED)
        stored_text = recognized_text  # Store recognized speech for submission
    except sr.UnknownValueError:
        audio_text.config(state=tk.NORMAL)
        audio_text.delete(1.0, tk.END)
        audio_text.insert(tk.END, "Sorry, could not understand audio.")
        audio_text.config(state=tk.DISABLED)
        stored_text = ""
    except sr.RequestError:
        audio_text.config(state=tk.NORMAL)
        audio_text.delete(1.0, tk.END)
        audio_text.insert(tk.END, "Sorry, there was an error with the speech recognition service.")
        audio_text.config(state=tk.DISABLED)
        stored_text = ""

def on_submit():
    remember = open('output.txt','w')
    global stored_text
    typed_text = get_text()
    if stored_text:  # If speech was recognized
        print("Recognized Speech:", stored_text)  # Use recognized text for further processing
        remember.write(stored_text)
    else:
        print("Stored Text:", typed_text)  # Use the typed text for further processing
        remember.write(typed_text)
    remember.close()

root = tk.Tk()
root.title("Text/Speech Input")

# Entry for typing text
text_entry_label = tk.Label(root, text="Enter text:")
text_entry_label.pack()
text_entry = tk.Entry(root)
text_entry.pack()

# Button to recognize speech
speech_input_button = tk.Button(root, text="Recognize Speech", command=recognize_speech)
speech_input_button.pack()

# Button to submit
submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.pack()

# Display recognized or entered text
result_label = tk.Label(root, text="", wraplength=300)
result_label.pack()

# Text area for displaying recognized speech
audio_text_label = tk.Label(root, text="Recognized Text:")
audio_text_label.pack()
audio_text = tk.Text(root, height=5, width=40, state=tk.DISABLED)
audio_text.pack()

# Note for further processing
note_label = tk.Label(root, text="Close the window after submitting for further processing", font=("Arial", 10), fg="blue")
note_label.pack()

root.mainloop()


model = KeyBERT(model="distilbert-base-nli-mean-tokens")
docfile = open('output.txt','r')
doc = docfile.read()
#doc = text_input
print(doc)
x = model.extract_keywords(
    doc,
    #candidates=["buildings","grasslands","water","forest"],
    #top_n=2,
    keyphrase_ngram_range=(1, 1),
    stop_words="english",
)
print(x)

def geocode(address):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Example Usage for Geocoding
address_to_geocode = x[0][0]
geocoding_result = geocode(address_to_geocode)
print("Geocoding Result:")
print(geocoding_result)
print(geocoding_result[0]['lat'])
print(float(geocoding_result[0]['lon']))

def fetch_area_polygon(lat, lon, radius):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json];
        (
            way
            (around:{radius},{lat},{lon})
            ["building"="yes"];
            >;
        );
        out geom;
    """
    response = requests.post(overpass_url, data=overpass_query)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def display_area_polygon_on_map(polygon_data):
    print(polygon_data)
    map_object = folium.Map(location=[polygon_data['elements'][0]['lat'], polygon_data['elements'][0]['lon']], zoom_start=15)

    for element in polygon_data['elements']:
        if 'tags' in element and 'building' in element['tags']:
            folium.Polygon(locations=[(node['lat'], node['lon']) for node in element['geometry']], color='blue', fill=True, fill_opacity=0.4).add_to(map_object)

    return map_object

# Example Usage
center_lat = float(geocoding_result[0]['lat'])
center_lon = float(geocoding_result[0]['lon'])
search_radius = 500  # in meters

area_polygon_data = fetch_area_polygon(center_lat, center_lon, search_radius)

if area_polygon_data:
    map_object_polygon = display_area_polygon_on_map(area_polygon_data)
    saving_path = 'F:/New folder/area_polygon_map.html'
    map_object_polygon.save(saving_path)
    webbrowser.open('file://'+saving_path)

