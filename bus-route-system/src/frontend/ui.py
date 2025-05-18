from streamlit import st
from src.backend.data_manager import DataManager
from src.backend.route_optimizer import RouteOptimizer

data_manager = DataManager()
route_optimizer = RouteOptimizer()

def display_routes(routes):
    st.title("Bus Routes")
    for route in routes:
        st.subheader(f"Route: {route['name']}")
        st.write(f"Stops: {', '.join(route['stops'])}")

def request_stop():
    st.sidebar.header("Request a Stop")
    stop_name = st.sidebar.text_input("Enter Stop Name")
    if st.sidebar.button("Request"):
        if stop_name:
            # Logic to handle stop request
            st.success(f"Stop '{stop_name}' requested successfully!")
        else:
            st.error("Please enter a stop name.")