import os
import re
import json
import asyncio
import argparse
from joplin_api import JoplinApi

TOKEN ="dd17a885a394a1c18f66a23a5578cde0200f4177bca0eb7ad8cb1b60a25b402e48942740e59a8522222b918c8d202e9e871e22992d18ad3df8ec6ad6d13e8c7c"
current_dir = os.getcwd()

def parse_options():
    parser = argparse.ArgumentParser(description="Market Toolkit pdf report generator.")

    parser.add_argument(
        "-t",
        "--token",
        dest="joplin_token",
        required=True,
        help="Get this token from Web Clipper settings in Joplin App.",
    )

    return parser.parse_args()
    
async def get_my_notes(joplin):
    notes = await joplin.get_notes()
    return notes

async def get_my_folders(joplin):
    notes = await joplin.get_folders()
    return notes

def get_folder_names(folders):
    folder_names = []
    for folder in folders:
        folder_names.append(folder['title'])

    return folder_names

def find_position_in_list(parsed_list, item_in_search):
    return (parsed_list.index(item_in_search))

async def main(options):
    joplin = JoplinApi(token=options.joplin_token)

    notes = await get_my_notes(joplin)
    folders = await get_my_folders(joplin)

    folders_json = folders.json()
    notes_json = notes.json()

    folder_names = get_folder_names(folders_json)
    print(folder_names)
    print("Please choose the folder to parse:")
    folder_to_parse = input()

    folder_index = find_position_in_list(folder_names, folder_to_parse)

    resource_folders = folders_json[folder_index]["children"]

    output_dir = os.path.join(current_dir, 'output', folder_to_parse)

    for i in range(len(resource_folders)):
        resource = resource_folders[i]
        resource_title = resource["title"]
        resource_id = resource["id"]

        folder_path = os.path.join(output_dir, resource_title)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    for folder in resource_folders:
        folder_path = os.path.join(output_dir, folder["title"])
        notes_list = list(filter(lambda notes: notes['parent_id'] == folder["id"], notes_json))

        for note in notes_list:
            note_title = note['title']
            note_id = note['id']
            note_parent_id = note['parent_id']
            note_created_at = note['created_time']
            note_body = note['body']

            file_path = os.path.join(folder_path, re.sub(r'[^\w]', '-', note_title))
            with open(f'{file_path}.md','wb') as note:
                s = f"""
title: {note_title}
id: {note_id}
parent_id: {note_parent_id}
created_at: {note_created_at}
---

{note_body}
                """
                note.write(s.encode("utf-8"))

if __name__ == "__main__":
    cli_options = parse_options()
    
    asyncio.run(
        main(cli_options)
    )