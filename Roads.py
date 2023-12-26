import requests
import folium

def fetch_roads_data_around_hyderabad():
    # Central coordinates of Hyderabad
    central_lat = 17.4967965
    central_lon = 78.3928008
    radius = 1000  # Radius in meters (adjust as needed)

    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
        [out:json];
        (
          way["highway"](around:{radius},{central_lat},{central_lon});
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

def save_roads_map_to_html(roads_data):
    if 'elements' in roads_data:
        map_object = folium.Map(location=[17.385044, 78.486671], zoom_start=14)  # Centered around Hyderabad

        for element in roads_data['elements']:
            if 'geometry' in element:
                locations = [(node['lat'], node['lon']) for node in element['geometry']]
                folium.PolyLine(locations=locations, color='brown').add_to(map_object)

        map_object.save('roads_map_around_hyderabad.html')
        print("Map saved as 'roads_map_around_hyderabad.html'")
    else:
        print("No roads data found.")

# Example Usage
roads_data = fetch_roads_data_around_hyderabad()

if roads_data:
    save_roads_map_to_html(roads_data)