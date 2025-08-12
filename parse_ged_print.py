from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from gedcom.parser import Parser
from gedcom.tags import GEDCOM_TAG_FAMILY_SPOUSE, GEDCOM_TAG_FAMILY_CHILD, GEDCOM_TAG_HUSBAND, GEDCOM_TAG_WIFE
from gedcom.tags import GEDCOM_TAG_CHILD
import os

# Path to your GEDCOM file
gedcom_file = "/Users/dpetrie/Petrie Family Tree_2025-08-04.ged"
output_dir = "gedcom_chunks"
os.makedirs(output_dir, exist_ok=True)

# Initialize parser
gedcom_parser = Parser()
gedcom_parser.parse_file(gedcom_file)
root_child_elements = gedcom_parser.get_root_child_elements()
element_dict = gedcom_parser.get_element_dictionary()

def get_family_members(sub_element):
    family_id = subelement.get_value()
    family_element = element_dict.get(family_id)

    for child in family_element.get_child_elements():
        tag = child.get_tag()
        if tag in ["HUSB", "WIFE", "CHIL"]:
            indiv = element_dict.get(child.get_value())
            if isinstance(indiv, IndividualElement):
                name = " ".join(indiv.get_name())
            else:
                name = "(Unknown)"

            if tag == "HUSB":
                role = "Husband"
            elif tag == "WIFE":
                role = "Wife"
            elif tag == "CHIL":
                role = "Child"
            else:
                role = tag  # fallback, in case other roles exist

            print(f"{role}: {name}")
                        
for element in root_child_elements:

    # Is the `element` an actual `IndividualElement`? (Allows usage of extra functions such as `surname_match` and `get_name`.)
    if isinstance(element, IndividualElement):
        child_elements = element.get_child_elements()

        # Unpack the name tuple
        (first, last) = element.get_name()

        # Print the first and last name of the found individual
        print("\nNAME:" + first + " " + last)

        for subelement in child_elements:
            print(f"  Sub-element tag: {subelement.get_tag()}")

            if subelement.get_tag() == "FAMS" or subelement.get_tag() == "FAMC":
                    notes = get_family_members(subelement)

                # if family_element:
                #     print(f"  Family ID: {family_id}")
                #     # Process family element as needed
                #     for family_member in family_element.get_child_elements():
                #         role = family_member.get_tag()
                #         indiv = element_dict.get(family_member.get_value())
                #         if isinstance(indiv, IndividualElement):
                #             (first, last) = indiv.get_name() if indiv else ("Unknown", "Unknown")
                #             print(f" {first} {last} {role}")
#                        print(f"    Individual Name: {indiv.get_name() if indiv else 'Unknown'}")
                        # You can further process family members if needed
                    # For example, you can extract family members or events here
#                    members = gedcom_parser.get_family_members(family_element)
#                    for member in members:
#                        print(f" - {member.get_name()}")
                    

#         spouse_families = gedcom_parser.get_families(element, family_type=GEDCOM_TAG_FAMILY_SPOUSE)

#         for family in spouse_families:
#             # Access information about the family (e.g., ID, events, members)
#             print(f"Family ID: {family.get_pointer()}")
#             # Example: Get family members
#             family_members = gedcom_parser.get_family_members(family)
#             for member in family_members:
# #                print(f"  Member: {member.get_name()}")
#                 for child in family.get_child_elements():
#  #                   print(f"  Child:  (ID: {child.get_value()})")
#  #                   print(f" {member.get_pointer()} ")
#                     if child.get_value() == member.get_pointer():
#                         role = child.get_tag()
#                         if role in ["HUSB", "WIFE", "CHIL"]:
#                             print(f" Member: {member.get_name()} Role: {role})")
              

