import ifcopenshell
import tkinter as tk
from tkinter import filedialog, messagebox


def filter_ifc_file(input_file, output_file, story_to_keep):
    # Open the IFC file
    ifc_file = ifcopenshell.open(input_file)

    # Get all elements in the IFC file
    elements = ifc_file.by_type('IfcProduct')

    # Get the specified story
    stories = ifc_file.by_type('IfcBuildingStorey')
    story_ids = [story.id() for story in stories if story.Name == story_to_keep]

    if not story_ids:
        print(f"No story found with the name '{story_to_keep}'.")
        return

    # Filter elements
    filtered_elements = []
    original_site = None
    for element in elements:
        # Check if the element is a slab, contains "Dekke" or "Dekker" in its name or layer (case-insensitive), or is an IfcSite
        name = element.Name.lower() if element.Name else ""
        if element.is_a('IfcSite'):
            original_site = element
        if (element.is_a('IfcSlab') or
                'dekke' in name or 'dekker' in name or
                any('dekke' in layer.Name.lower() or 'dekker' in layer.Name.lower() for layer in element.HasAssociations
                    if layer.is_a('IfcPresentationLayerAssignment'))):
            # Check if the element is on the specified story
            if any(rel.RelatingStructure.id() in story_ids for rel in element.ContainedInStructure):
                filtered_elements.append(element)

    # Create a new IFC file and add the filtered elements
    new_ifc_file = ifcopenshell.file(schema=ifc_file.schema)
    if original_site:
        new_ifc_file.add(original_site)
        # Add relationships of the original site
        for rel in ifc_file.get_inverse(original_site):
            new_ifc_file.add(rel)
    for element in filtered_elements:
        new_ifc_file.add(element)

    # Write the new IFC file to disk
    new_ifc_file.write(output_file)


def select_story(stories):
    def on_select(event):
        selected_story.set(listbox.get(listbox.curselection()))
        root.quit()

    root = tk.Tk()
    root.title("Select Building Story")

    selected_story = tk.StringVar()

    listbox = tk.Listbox(root)
    listbox.pack(fill=tk.BOTH, expand=True)

    for story in stories:
        listbox.insert(tk.END, story)

    listbox.bind('<<ListboxSelect>>', on_select)

    root.mainloop()

    return selected_story.get()


def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open file dialog to select input file
    input_file = filedialog.askopenfilename(title="Select input IFC file", filetypes=[("IFC files", "*.ifc")])
    if not input_file:
        print("No input file selected.")
        return

    # Open file dialog to select output file
    output_file = filedialog.asksaveasfilename(title="Select output IFC file", defaultextension=".ifc",
                                               filetypes=[("IFC files", "*.ifc")])
    if not output_file:
        print("No output file selected.")
        return

    # Extract building stories from the IFC file
    ifc_file = ifcopenshell.open(input_file)
    stories = [story.Name for story in ifc_file.by_type('IfcBuildingStorey')]

    # Prompt to select the story to keep
    story_to_keep = select_story(stories)
    if not story_to_keep:
        print("No story selected.")
        return

    # Filter the IFC file
    filter_ifc_file(input_file, output_file, story_to_keep)
    print(f"Filtered IFC file saved to {output_file}")


# Run the file selection dialog
select_files()
