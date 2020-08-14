import re
import asyncio

async def get_notes(joplin):
    notes = await joplin.get_notes()
    return notes

async def get_folders(joplin):
    notes = await joplin.get_folders()
    return notes

def get_folder_names(folders):
    folder_names = []
    for folder in folders:
        folder_names.append(folder['title'])

    return folder_names

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