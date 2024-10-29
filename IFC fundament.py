import ifcopenshell
from tkinter import Tk, filedialog


def remove_non_slab_elements(ifc_file_path, output_file_path):
    # Open the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Get all the building stories
    stories = ifc_file.by_type("IfcBuildingStorey")

    # Sort stories by elevation and get the two lowest stories
    sorted_stories = sorted(stories, key=lambda s: s.Elevation)
    lowest_stories = sorted_stories[:2]

    # Get the slabs in the two lowest stories
    slabs_to_keep = []
    for story in lowest_stories:
        for rel in story.ContainsElements:
            for element in rel.RelatedElements:
                if element.is_a("IfcSlab"):
                    slabs_to_keep.append(element)

    # Create a set of elements to keep (including their related elements)
    elements_to_keep = set(slabs_to_keep)
    for slab in slabs_to_keep:
        if hasattr(slab, 'HasAssociations'):
            for rel in slab.HasAssociations:
                elements_to_keep.add(rel)
        if hasattr(slab, 'HasAssignments'):
            for rel in slab.HasAssignments:
                elements_to_keep.add(rel)
        if hasattr(slab, 'HasCoverings'):
            for rel in slab.HasCoverings:
                elements_to_keep.add(rel)
        if hasattr(slab, 'HasOpenings'):
            for rel in slab.HasOpenings:
                elements_to_keep.add(rel)
        if hasattr(slab, 'HasProjections'):
            for rel in slab.HasProjections:
                elements_to_keep.add(rel)
        if hasattr(slab, 'HasStructuralMember'):
            for rel in slab.HasStructuralMember:
                elements_to_keep.add(rel)

    # Add elements containing "Dekke" or "Dekker" in Type name or Layer to the set of elements to keep
    for element in ifc_file.by_type("IfcProduct"):
        if hasattr(element, 'Name') and element.Name and ("Dekke" in element.Name or "Dekker" in element.Name):
            elements_to_keep.add(element)
        if hasattr(element, 'LayerAssignment'):
            for layer in element.LayerAssignment:
                if layer.Name and ("Dekke" in layer.Name or "Dekker" in layer.Name):
                    elements_to_keep.add(element)

    # Add IfcSite and IfcBuildingStorey to the set of elements to keep
    for site in ifc_file.by_type("IfcSite"):
        elements_to_keep.add(site)
    for story in ifc_file.by_type("IfcBuildingStorey"):
        elements_to_keep.add(story)

    # Remove all other elements from the IFC file
    for element in ifc_file.by_type("IfcProduct"):
        if element not in elements_to_keep:
            ifc_file.remove(element)

    # Write the modified IFC file to the output path
    ifc_file.write(output_file_path)


# Open a file dialog to select the input and output IFC files
root = Tk()
root.withdraw()  # Hide the root window

input_file_path = filedialog.askopenfilename(title="Select IFC Input File", filetypes=[("IFC files", "*.ifc")])
output_file_path = filedialog.asksaveasfilename(title="Select IFC Output File", defaultextension=".ifc",
                                                filetypes=[("IFC files", "*.ifc")])

# Run the function with the selected file paths
if input_file_path and output_file_path:
    remove_non_slab_elements(input_file_path, output_file_path)
