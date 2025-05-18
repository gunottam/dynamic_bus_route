def create_map(location, zoom_start=13):
    import folium
    return folium.Map(location=location, zoom_start=zoom_start)

def add_route_to_map(map_obj, route, color='blue'):
    folium.PolyLine(locations=route, color=color, weight=5).add_to(map_obj)