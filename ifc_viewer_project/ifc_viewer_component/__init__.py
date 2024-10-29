import streamlit.components.v1 as components

# Declare the component
_component_func = components.declare_component(
    "web_ifc_viewer",
    path="frontend/build",  # Path to the build directory of your frontend
)

def web_ifc_viewer(url: str):
    # Call the component and pass the URL
    _component_func(url=url)
