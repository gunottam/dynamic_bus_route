import streamlit as st
from backend.data_manager import DataManager
from backend.route_optimizer import RouteOptimizer
from frontend.ui import display_routes, request_stop

def main():
    st.title("Dynamic Bus Route System")
    
    data_manager = DataManager()
    route_optimizer = RouteOptimizer()

    # Load existing data
    bus_stops = data_manager.load_data()

    # User input for stop requests
    requested_stops = request_stop(bus_stops)

    # Optimize route based on user requests
    optimized_route = route_optimizer.optimize_route(requested_stops)

    # Display the optimized routes
    display_routes(optimized_route)

if __name__ == "__main__":
    main()