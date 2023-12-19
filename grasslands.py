import requests
import folium
import webbrowser

def fetch_grasslands_data_around_telangana():
   
    central_lat = 17.360589
    central_lon = 78.4740613
    radius = 70000  

    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
        [out:json];
        (
          way["natural"="grassland"](around:{radius},{central_lat},{central_lon});
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

def display_grasslands_on_map(grasslands_data):
    if 'elements' in grasslands_data:
        map_object = folium.Map(location=[17.360589, 78.4740613], zoom_start=13) 

        for element in grasslands_data['elements']:
            if 'geometry' in element:
                locations = [(node['lat'], node['lon']) for node in element['geometry']]
                folium.Polygon(locations=locations, color='green', fill=True, fill_opacity=0.7).add_to(map_object)

        return map_object
    else:
        print("No grasslands data found.")
        return None


grasslands_data = fetch_grasslands_data_around_telangana()

if grasslands_data:
    map_object_grasslands = display_grasslands_on_map(grasslands_data)
    map_object_grasslands.save('grasslands_map_around_hyderabad.html')
    webbrowser.open('grasslands_map_around_hyderabad.html')