import ifcopenshell
import streamlit as st
import os
import tempfile


def filter_ifc_file(input_file, output_file, stories_to_keep, types_to_keep, keywords, filter_option):
    # Open the IFC file
    ifc_file = ifcopenshell.open(input_file)

    # Get all elements in the IFC file
    elements = ifc_file.by_type('IfcProduct')

    # Get the specified stories
    if "All Stories" in stories_to_keep:
        story_ids = [story.id() for story in ifc_file.by_type('IfcBuildingStorey')]
    else:
        story_ids = [story.id() for story in ifc_file.by_type('IfcBuildingStorey') if story.Name in stories_to_keep]

    if not story_ids:
        st.error(f"No stories found with the names '{stories_to_keep}'.")
        return

    # Filter elements
    filtered_elements = []
    original_site = None
    for element in elements:
        # Check if the element is an IfcSite
        if element.is_a('IfcSite'):
            original_site = element

        # Check if the element matches the selected types and/or keywords based on filter_option
        name = element.Name.lower() if element.Name else ""
        matches_type = any(element.is_a(type_name) for type_name in types_to_keep)
        matches_keyword = any(keyword.lower() in name for keyword in keywords)

        if filter_option == "IFC types and keywords":
            if matches_type and matches_keyword:
                # Check if the element is on the specified stories
                if any(rel.RelatingStructure.id() in story_ids for rel in element.ContainedInStructure):
                    filtered_elements.append(element)
        elif filter_option == "IFC types only":
            if matches_type:
                # Check if the element is on the specified stories
                if any(rel.RelatingStructure.id() in story_ids for rel in element.ContainedInStructure):
                    filtered_elements.append(element)
        elif filter_option == "Keywords only":
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
        # Copy all properties and relationships of the element
        for rel in ifc_file.get_inverse(element):
            new_ifc_file.add(rel)

    # Write the new IFC file to disk
    new_ifc_file.write(output_file)


def main():
    st.title("IFC File Filter")

    input_file = st.file_uploader("Upload input IFC file", type=["ifc"])

    if input_file:
        # Save uploaded file to a temporary location
        with open("temp.ifc", "wb") as f:
            f.write(input_file.getbuffer())

        # Extract building stories from the IFC file
        ifc_file = ifcopenshell.open("temp.ifc")
        stories = [story.Name for story in ifc_file.by_type('IfcBuildingStorey')]
        stories.insert(0, "All Stories")  # Add "All Stories" option

        # Prompt to select the stories to keep
        stories_to_keep = st.multiselect("Select Building Stories to keep", stories)

        # Prompt to choose filter option
        filter_option = st.radio("Choose filter option", ["IFC types and keywords", "IFC types only", "Keywords only"])

        types_to_keep = []
        keywords = []

        if filter_option == "IFC types and keywords" or filter_option == "IFC types only":
            # Extract IFC types from the IFC file
            types = set(element.is_a() for element in ifc_file.by_type('IfcProduct'))

            # Prompt to select the types to keep
            types_to_keep = st.multiselect("Select IFC Types to keep", list(types))

        if filter_option == "IFC types and keywords" or filter_option == "Keywords only":
            # Prompt to enter keywords to filter objects
            keywords = st.text_area("Enter keywords to filter objects (comma-separated)").split(',')

        # Construct the suffix based on selected options
        suffix_parts = []
        if types_to_keep:
            suffix_parts.append("_".join(types_to_keep))
        if keywords:
            suffix_parts.append("_".join(keywords))
        suffix = "_".join(suffix_parts)

        # Use a temporary file for output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_output:
            output_filename = temp_output.name

        original_filename = os.path.splitext(input_file.name)[0]
        download_filename = f"{original_filename}_{suffix}.ifc"

        if st.button("Filter IFC File"):
            filter_ifc_file("temp.ifc", output_filename, stories_to_keep, types_to_keep, keywords, filter_option)

            with open(output_filename, 'rb') as f:
                st.download_button(
                    label="Download filtered IFC file",
                    data=f,
                    file_name=download_filename,
                    mime="application/octet-stream"
                )


if __name__ == "__main__":
    main()
