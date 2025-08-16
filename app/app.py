
import streamlit as st
from genetic_algorithm_advanced import AdvancedRouteOptimizer, OptimizationRequest, WasteType, Vehicle, WasteClassification
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components
import random

# --- Improved Custom CSS for a clean, soft look ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(120deg, #f8fafc 0%, #e9f5f9 100%) !important;
    }
    .stApp {
        background: transparent !important;
    }
    .main {
        background-color: rgba(255,255,255,0.95) !important;
        border-radius: 18px;
        padding: 2rem;
        box-shadow: 0 4px 32px 0 rgba(0,0,0,0.07);
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #6dd5ed 0%, #2193b0 100%);
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 2px 8px 0 rgba(33,147,176,0.10);
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%);
        color: #fff;
        transform: scale(1.04);
    }
    .stNumberInput>div>input {
        border-radius: 6px;
        border: 1.5px solid #2193b0;
        background: #fafdff;
        font-size: 1.05rem;
    }
    .stSelectbox>div>div {
        border-radius: 6px;
        border: 1.5px solid #2193b0;
        background: #222 !important;
        color: #fff !important;
        font-size: 1.05rem;
    }
    .stAlert {
        border-radius: 12px;
        box-shadow: 0 2px 12px 0 rgba(33,147,176,0.08);
    }
    label, .stNumberInput label, .stSelectbox label {
        color: #2193b0 !important;
        font-weight: 600 !important;
        font-size: 1.08rem !important;
        margin-bottom: 0.2rem !important;
    }
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, #6dd5ed 0%, #2193b0 100%);
        margin: 2rem 0 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
<h2 style='color:#2193b0;'>Navigation</h2>
<ul style='font-size:1.1rem;list-style:none;padding-left:0;'>
    <li><a href='#waste-classification' style='color: #fff; text-decoration: none;'>Waste Classification</a></li>
    <li><a href='#route-optimization' style='color: #fff; text-decoration: none;'>Route Optimization</a></li>
    <li><a href='#visualization' style='color: #fff; text-decoration: none;'>Visualization</a></li>
</ul>
<hr>
""", unsafe_allow_html=True)

def fuzzy_risk_score(pH, flash_point, toxicity):
    risk = 0
    if pH < 3 or pH > 11:
        risk += 1
    if flash_point < 37:
        risk += 1
    if toxicity.lower() == "high":
        risk += 1
    if risk == 0:
        return "Low"
    elif risk == 1:
        return "Medium"
    else:
        return "High"

def plot_route(route_nodes):
    # Now with 3 disposal nodes and improved interactivity
    all_nodes = [
        "Source", "Inspection A", "Inspection B", "Inspection C",
        "Node X", "Node Y", "Node Z", "Node W", "Disposal A", "Disposal B", "Disposal C"
    ]
    all_edges = [
        ("Source", "Inspection A"), ("Source", "Inspection B"), ("Source", "Inspection C"),
        ("Inspection A", "Node X"), ("Inspection B", "Node Y"), ("Inspection C", "Node Z"),
        ("Node X", "Disposal A"), ("Node Y", "Disposal B"), ("Node Z", "Disposal C"),
        ("Source", "Node W"), ("Node W", "Disposal A"), ("Node W", "Disposal B"), ("Node W", "Disposal C")
    ]
    route_edges = [(route_nodes[i], route_nodes[i+1]) for i in range(len(route_nodes)-1)]

    net = Network(height="400px", width="100%", directed=True, notebook=False)
    for node in all_nodes:
        color = "deepskyblue" if node in route_nodes else "lightgray"
        size = 30 if node in route_nodes else 20
        net.add_node(node, label=node, color=color, size=size, physics=True)
    for edge in all_edges:
        color = "orange" if edge in route_edges else "#cccccc"
        width = 4 if edge in route_edges else 1
        net.add_edge(edge[0], edge[1], color=color, width=width)

    net.set_options('''
    var options = {
      "nodes": {"font": {"size": 18}, "physics": true, "shadow": true},
      "edges": {"arrows": {"to": {"enabled": true}}, "smooth": true},
      "interaction": {"hover": true, "multiselect": true, "navigationButtons": true}
    }
    ''')
    net.save_graph("route_graph.html")
    HtmlFile = open("route_graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=450)

st.markdown('<h1 style="color:#2193b0;font-weight:900;text-shadow:1px 1px 8px #6dd5ed;">♻️ Smart Hazardous Waste Classifier & Route Optimizer</h1>', unsafe_allow_html=True)
st.markdown('<h4 style="color:#2193b0;">A modern tool for safe, efficient hazardous waste management</h4>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)




# --- Input Section: Waste Properties ---
st.markdown('<h3 style="color:#2193b0;">🧪 Waste Properties</h3>', unsafe_allow_html=True)
st.markdown('<div style="color:#888;font-size:0.98rem;margin-bottom:0.5rem;">Enter the following details:</div>', unsafe_allow_html=True)
pH = st.number_input("pH Level (0-14)", min_value=0.0, max_value=14.0, value=7.0, key="ph_input")
flash_point = st.number_input("Flash Point (°C)", min_value=0, max_value=200, value=50, key="flash_point_input")
# Fix: always enable toxicity selectbox
toxicity = st.selectbox("Toxicity Level", ["Low", "Medium", "High"], key="toxicity_select", index=0)
st.markdown('<hr>', unsafe_allow_html=True)

# --- Input Section: Vehicle & Quantity ---
st.markdown('<h3 style="color:#2193b0;">🚚 Vehicle & Quantity</h3>', unsafe_allow_html=True)
st.markdown('<div style="color:#888;font-size:0.98rem;margin-bottom:0.5rem;">Specify vehicle and waste details:</div>', unsafe_allow_html=True)
vehicle_capacity = st.number_input("Vehicle Capacity (kg)", min_value=1, max_value=10000, value=1000, key="vehicle_capacity")
waste_quantity = st.number_input("Waste Quantity (kg)", min_value=1, max_value=10000, value=500, key="waste_quantity")
st.markdown('<hr>', unsafe_allow_html=True)

if st.button("✨ Classify & Optimize Route"):
    # Map user input to WasteType
    if toxicity == "High":
        if flash_point <= 60:
            waste_type = WasteType.FLAMMABLE
        else:
            waste_type = WasteType.TOXIC
    elif pH <= 2.0 or pH >= 12.5:
        waste_type = WasteType.CORROSIVE
    else:
        waste_type = WasteType.GENERAL

    st.markdown(
        f'<div style="background:linear-gradient(90deg,#2193b0,#6dd5ed);color:#fff;padding:0.9rem 1.2rem;border-radius:10px;font-size:1.1rem;margin-bottom:0.5rem;box-shadow:0 2px 8px 0 rgba(33,147,176,0.10);font-weight:bold;">'
        f'Waste type: {waste_type}'
        '</div>',
        unsafe_allow_html=True
    )

    # Prepare advanced optimizer request
    vehicle = Vehicle(vehicle_capacity)
    waste_classification = WasteClassification(waste_type, waste_quantity)
    request = OptimizationRequest(
        source_location="source",
        destination_location="disposal",
        waste_classification=waste_classification,
        vehicle=vehicle
    )
    optimizer = AdvancedRouteOptimizer()

    # Find the best route using a simple GA loop
    # For demo: generate a population of random valid routes, pick the best by fitness
    def generate_valid_route():
        # Build a valid path from Source to Disposal A using only allowed edges
        # Network: Source -> Inspection A -> Node X -> Disposal A
        route = ["Source"]
        if random.random() < 0.7:
            route.append("Inspection A")
            if random.random() < 0.7:
                route.append("Node X")
        else:
            route.append("Node W")
        route.append("Disposal A")
        # Validate route: all consecutive pairs must be valid edges
        valid_edges = {
            ("Source", "Inspection A"), ("Source", "Node W"),
            ("Inspection A", "Node X"), ("Node X", "Disposal A"),
            ("Node W", "Disposal A")
        }
        for i in range(len(route) - 1):
            if (route[i], route[i+1]) not in valid_edges:
                return None
        return route

    best_route = None
    best_fitness = -float('inf')
    best_cost = None
    for _ in range(100):
        route = generate_valid_route()
        if not route:
            continue
        node_map = {
            "Source": "source",
            "Inspection A": "inspection_a",
            "Node X": "node_1",
            "Node W": "node_w",
            "Disposal A": "disposal",
        }
        key_route = [node_map.get(n, n.lower().replace(' ', '_')) for n in route]
        fitness = optimizer._calculate_fitness(key_route, request)
        # Calculate cost
        total_cost = 0
        for i in range(len(key_route) - 1):
            a, b = key_route[i], key_route[i+1]
            edge = optimizer.network["distances"].get((a, b)) or optimizer.network["distances"].get((b, a))
            if edge:
                total_cost += edge["distance"] * 10
        if fitness > best_fitness:
            best_fitness = fitness
            best_route = route
            best_cost = total_cost



    if best_route:
        best_route_str = ' -> '.join(best_route)
        blue_box = 'background:linear-gradient(90deg,#36d1c4,#5b86e5);color:white;padding:1rem 1.5rem;border-radius:12px;font-size:1.1rem;margin-bottom:0.5rem;box-shadow:0 2px 8px 0 rgba(91,134,229,0.10);font-weight:bold;'
        st.markdown(
            f'<div style="{blue_box}">Waste type: {waste_type}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="{blue_box}"><b>Best Route:</b> {best_route_str}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="{blue_box}"><b>Fitness Score:</b> {best_fitness:.4f} (higher is better)</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="{blue_box}"><b>Total cost:</b> {best_cost} units</div>',
            unsafe_allow_html=True
        )
        # Fuzzy risk score output
        risk_score = fuzzy_risk_score(pH, flash_point, toxicity)
        st.markdown(
            f'<div style="{blue_box}">🚨 <b>Fuzzy Risk Level:</b> <span style="font-size:1.2rem;">{risk_score}</span></div>',
            unsafe_allow_html=True
        )
        # Route graph visualization
        st.markdown('<h3 style="color:#36d1c4;">🗺️ Route Visualization</h3>', unsafe_allow_html=True)
        plot_route(best_route)
    else:
        st.error("No valid route could be generated. Please check your input values.")