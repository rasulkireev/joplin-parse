import os
import re
import asyncio
from typing import List
from joplin_api import JoplinApi

async def download_resource(joplin, resource, resource_location):
        downloaded_resource = await joplin.download_resources(resource['id'])
        save_path = os.path.join(resource_location, f"{resource['id']}.{resource['file_extension']}")

        if not os.path.exists(resource_location):
            os.makedirs(resource_location)

        with open(save_path, "wb") as f:
            f.write(downloaded_resource.content)

        return downloaded_resource

def get_folder_names(folders):
    folder_names = []
    for folder in folders:
        folder_names.append(folder['title'])

    return folder_names

def has_children(folder: dict) -> bool:
    """Tells us whether a folder has a subfolder.

    Args:
        folder (dict): Folder object.

    Returns:
        bool: Boolean
    """
    try:
        folder['children']
        return True
    except KeyError:
        return False
        
def find_position_in_list(parsed_list, item_in_search):
    return (parsed_list.index(item_in_search))

def search_for_joplin_links(text):
    internal_links = re.findall("\(:/.+\)", text)

    link_ids = []
    for link in internal_links:
        note_id = re.search("(?<=\(:\/).+?(?=\))", link).group()
        link_ids.append(note_id)
    
    return link_ids

def find_linked_note(notes, link):
    for note in notes:
        if note['id'] == link:
            linked_note = note
    
    return linked_note

def remove_spaces(text: str) -> str:
    """Replace every non-word character (\W) with a dash.
    Convinient when you need to make a URL slug.

    Args:
        text (str): Text you want

    Returns:
        str: [description]
    """
    new_text = re.sub(r'[^\w]', '-', text)

    return new_text

def search_and_replace_joplin_note_links(text: str, notes_dict: dict) -> str:
    """Goes through a block of text and replaces all the internal links with valid syntax

    Example:
        from: "(:/f9cb6c07fc8d48c2929eef772911bd1f)"
        to: (./valid-link.md)

    Args:
        text (str): Text you want to go through
        notes_dict (dict): Dictionary of all the joplin notes 

    Returns:
        str: Text with replaced links.
    """
    internal_links = re.findall("\(:/.+\)", text)
    
    for link_to_replace in internal_links:
        note_id_to_replace = re.search("(?<=\(:\/).+?(?=\))", link_to_replace).group()
        note_title_replaced = notes_dict[note_id_to_replace]
        new_link = remove_spaces(note_title_replaced)
        
        text = text.replace(link_to_replace, f"(./{new_link}.md)")
    
    return text    

def search_and_replace_joplin_resource_links(text: str, resources_types_dict: dict, resource_location: str) -> str:
    """Goes through a block of text and replaces all the internal links with valid syntax. For resources.

    Example:
        from: "(:/f9cb6c07fc8d48c2929eef772911bd1f)"
        to: (./valid-link.jpg)

    Args:
        text (str): Text you want to go through
        resrouces_types_dict (dict): Dictionary of all the resource, id pairs
        resource_location (str): Folder name where all resources are stored

    Returns:
        str: Text with replaced links.
    """
    internal_links = re.findall("\(:/.+\)", text)
    
    for link_to_replace in internal_links:
        resource_id = re.search("(?<=\(:\/).+?(?=\))", link_to_replace).group()        
        text = text.replace(link_to_replace, f"(../{resource_location}/{resource_id}.{resources_types_dict[resource_id]})")
    
    return text    

def generate_dict_with_folder_and_ids(folders):
    folders_dict = {}

    for folder in folders:
        folders_dict[folder['id']] = folder['title']

        if has_children(folder):
            folders = folder['children'] 
            for folder in folders:
                folders_dict[folder['id']] = folder['title']

                if has_children(folder):
                    folders = folder['children'] 
                    for folder in folders:
                        folders_dict[folder['id']] = folder['title']

                        if has_children(folder):
                            folders = folder['children'] 
                            for folder in folders:
                                folders_dict[folder['id']] = folder['title']
    return folders_dict

def generate_dict_with_all_notes_and_ids(notes):
    notes_dict = {}

    for note in notes:
        notes_dict[note['id']] = note['title']

    return notes_dict

def generate_dict_with_all_resources(resources: List) -> dict:
    resources_types_dict = {}

    for resource in resources:
        resources_types_dict[resource['id']] = resource['file_extension']

    return resources_types_dict

def get_folder_title(note: dict, folders_dict: dict) -> str:
    """Get the name of the folder, where note is located

    Args:
        note (dict): Note object.
        folders_dict (dict): Dictionary of all the folder IDs & Titles.

    Returns:
        str: Name of the folder.
    """
    folder_id = note['parent_id']
    folder_title = folders_dict[folder_id]
    
    return folder_title
