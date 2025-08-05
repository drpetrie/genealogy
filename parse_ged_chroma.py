from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
import chromadb
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

import os

# === CONFIGURATION ===
gedcom_file = "/Users/dpetrie/Petrie Family Tree_2025-08-04.ged"
collection_name = "gedcom_family"
chroma_dir = "/Users/dpetrie/chroma_store"  # Chroma persistent storage

# === Initialize GEDCOM Parser ===
gedcom_parser = Parser()
gedcom_parser.parse_file(gedcom_file)
elements = gedcom_parser.get_element_list()

# === Extract Residences ===
def extract_residences(element):
    """Extract RESI entries (residences) from raw sub-elements."""
    residences = []
    for sub in element.get_child_elements():
        if sub.get_tag() == "RESI":
            date = ""
            place = ""
            for child in sub.get_child_elements():
                if child.get_tag() == "DATE":
                    date = child.get_value()
                elif child.get_tag() == "PLAC":
                    place = child.get_value()
            if place:
                if date:
                    residences.append(f"{place} ({date})")
                else:
                    residences.append(place)
    return residences

def extract_notes(element, note_map):
    """Extract NOTE entries, resolving references."""
    notes = []
    for sub in element.get_child_elements():
        if sub.get_tag() == "NOTE":
            val = sub.get_value()
            if val and val.startswith("@") and val.endswith("@"):
                # It's a reference to a @NOTE@ record
                ref = val.strip("@")
                if ref in note_map:
                    notes.append(note_map[ref])
            else:
                # It's an inline note
                note_text = val or ""
                for child in sub.get_child_elements():
                    if child.get_tag() == "CONC":
                        note_text += child.get_value()
                    elif child.get_tag() == "CONT":
                        note_text += "\n" + (child.get_value() or "")
                notes.append(note_text.strip())
    return notes

def get_full_note_text(note_element):
    """Recursively extract all CONC and CONT text from a NOTE record."""
    text = ""

    def walk(element):
        nonlocal text
        for child in element.get_child_elements():
            tag = child.get_tag()
            val = child.get_value() or ""
            if tag == "CONC":
                text += val
            elif tag == "CONT":
                text += "\n" + val
            # Keep walking deeper in case CONT has its own CONC, etc.
            walk(child)

    walk(note_element)
    return text.strip()

def format_individual(ind, note_map):
    """Format individual data into plain text with residences."""
    name = ind.get_name()
    birth_data = ind.get_birth_data()
    death_data = ind.get_death_data()
    sex = ind.get_gender()
    residences = extract_residences(ind)
    notes = extract_notes(ind, note_map)

    output = f"Name: {name[0]} {name[1]}\n"
    output += f"Sex: {sex}\n"
    
    if birth_data:
        output += f"Born: {birth_data[0]}"
        if birth_data[1]:
            output += f" in {birth_data[1]}"
        output += "\n"
    
    if death_data:
        output += f"Died: {death_data[0]}"
        if death_data[1]:
            output += f" in {death_data[1]}"
        output += "\n"

    if residences:
        output += "\nPlaces of Residence:\n"
        for r in residences:
            output += f"  - {r}\n"

    if notes:
        output += "\nNotes:\n"
        for n in notes:
            output += f"  - {n}\n"

    return output.strip()

# === Set Up ChromaDB ===
print(chroma_dir)
chroma_client = chromadb.Client(chromadb.config.Settings(
    persist_directory=chroma_dir, is_persistent=True
))

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or load collection
collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_fn
)

# Create a dict of all NOTE records by pointer (e.g., N99)
note_map = {}
for element in elements:
    if element.get_tag() == "NOTE":
        pointer = element.get_pointer().strip("@") if element.get_pointer() else ""
        if pointer:  # Only store if it's a referenced note record
            note_map[pointer] = get_full_note_text(element)
        
# === Process Individuals into ChromaDB ===
count = 0
for element in elements:
    if isinstance(element, IndividualElement):
        doc_id = element.get_pointer().replace("@", "")
        content = format_individual(element, note_map)
        full_name = element.get_name()[0] + " " + element.get_name()[1]
        collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"name": full_name}]
        )
#        count += 1
#        if count >= 20:
#            break

# Optional: persist to disk
#chroma_client.persist()

print(f"✅ Embedded {len(collection.get()['ids'])} individuals into ChromaDB.")