import ifcopenshell
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


def filter_ifc_file(input_file, output_file, stories_to_keep, types_to_keep, keyword, filter_option):
    # Open the IFC file
    ifc_file = ifcopenshell.open(input_file)

    # Get all elements in the IFC file
    elements = ifc_file.by_type('IfcProduct')

    # Get the specified stories
    story_ids = [story.id() for story in ifc_file.by_type('IfcBuildingStorey') if story.Name in stories_to_keep]

    if not story_ids:
        print(f"No stories found with the names '{stories_to_keep}'.")
        return

    # Filter elements
    filtered_elements = []
    original_site = None
    for element in elements:
        # Check if the element is an IfcSite
        if element.is_a('IfcSite'):
            original_site = element

        # Check if the element matches the selected types and/or keyword based on filter_option
        name = element.Name.lower() if element.Name else ""
        matches_type = any(element.is_a(type_name) for type_name in types_to_keep)
        matches_keyword = keyword.lower() in name

        if filter_option == "IFC types and keyword":
            if matches_type and matches_keyword:
                # Check if the element is on the specified stories
                if any(rel.RelatingStructure.id() in story_ids for rel in element.ContainedInStructure):
                    filtered_elements.append(element)
        elif filter_option == "IFC types only":
            if matches_type:
                # Check if the element is on the specified stories
                if any(rel.RelatingStructure.id() in story_ids for rel in element.ContainedInStructure):
                    filtered_elements.append(element)
        elif filter_option == "Keyword only":
            if matches_keyword:
                # Check if the element is on the specified stories
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


def select_items(items, title):
    def on_select():
        selected_items.set([listbox.get(i) for i in listbox.curselection()])
        root.quit()

    root = tk.Tk()
    root.title(title)

    selected_items = tk.Variable()

    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
    listbox.pack(fill=tk.BOTH, expand=True)

    for item in items:
        listbox.insert(tk.END, item)

    button = tk.Button(root, text="Select", command=on_select)
    button.pack()

    root.mainloop()

    return selected_items.get()


def select_filter_option():
    def on_select():
        selected_option.set(listbox.get(listbox.curselection()))
        root.quit()

    root = tk.Tk()
    root.title("Select Filter Option")

    selected_option = tk.StringVar()

    options = ["IFC types and keyword", "IFC types only", "Keyword only"]

    listbox = tk.Listbox(root)
    listbox.pack(fill=tk.BOTH, expand=True)

    for option in options:
        listbox.insert(tk.END, option)

    button = tk.Button(root, text="Select", command=on_select)
    button.pack()

    root.mainloop()

    return selected_option.get()


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

    # Prompt to select the stories to keep
    stories_to_keep = select_items(stories, "Select Building Stories")
    if not stories_to_keep:
        print("No stories selected.")
        return

    # Prompt to choose filter option
    filter_option = select_filter_option()

    types_to_keep = []
    keyword = ""

    if filter_option == "IFC types and keyword" or filter_option == "IFC types only":
        # Extract IFC types from the IFC file
        types = set(element.is_a() for element in ifc_file.by_type('IfcProduct'))

        # Prompt to select the types to keep
        types_to_keep = select_items(types, "Select IFC Types")
        if not types_to_keep:
            print("No types selected.")
            return

    if filter_option == "IFC types and keyword" or filter_option == "Keyword only":
        # Prompt to enter a keyword to filter objects
        keyword = simpledialog.askstring("Input", "Enter a keyword to filter objects:")

    # Filter the IFC file
    filter_ifc_file(input_file, output_file, stories_to_keep, types_to_keep, keyword, filter_option)

    print(f"Filtered IFC file saved to {output_file}")


# Run the file selection dialog
select_files()
