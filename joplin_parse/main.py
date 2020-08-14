import os
import re
import json
import asyncio
import argparse
from joplin_api import JoplinApi
from joplin_parse.utils import get_notes, get_folders, get_folder_names, find_position_in_list

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
    
async def main(options):
    joplin = JoplinApi(token=options.joplin_token)

    all_notes = await get_notes(joplin)
    all_folders = await get_folders(joplin)

    folders_json = all_folders.json()
    notes_json = all_notes.json()

    parent_folder_names = get_folder_names(folders_json)
    print(parent_folder_names)
    print("Please choose the folder to parse:")
    folder_to_parse = input()

    folder_index = find_position_in_list(parent_folder_names, folder_to_parse)
    child_folders = folders_json[folder_index]["children"]

    output_dir = os.path.join(current_dir, 'output', folder_to_parse)

    for i in range(len(child_folders)):
        folder = child_folders[i]
        folder_title = folder["title"]
        folder_id = folder["id"]

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    for folder in child_folders:
        folder_title = folder["title"]
        notes_list = list(filter(lambda notes: notes['parent_id'] == folder["id"], notes_json))

        for note in notes_list:
            file_path = os.path.join(output_dir, re.sub(r'[^\w]', '-', note['title']))
            with open(f'{file_path}.md','wb') as md_note:
                s = f"""---
title: `{note['title']}`
category: {folder_title}
id: {note['id']}
parent_id: {note['parent_id']}
created_at: {note['created_time']}
---

{note['body']}
                """
                md_note.write(s.encode("utf-8"))

if __name__ == "__main__":
    cli_options = parse_options()
    
    asyncio.run(
        main(cli_options)
    )