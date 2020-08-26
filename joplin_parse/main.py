import os
import re
import json
import asyncio
import argparse
from joplin_api import JoplinApi
from joplin_parse.utils import (
    get_folder_names, 
    find_position_in_list, 
    remove_spaces,
    generate_dict_with_folder_and_ids,
    generate_dict_with_all_notes_and_ids,
    generate_dict_with_all_resources,
    search_and_replace_joplin_note_links,
    search_and_replace_joplin_resource_links,
    has_children,
    get_folder_title,
    download_resource
)

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

    all_notes = (await joplin.get_notes()).json()    
    all_folders = (await joplin.get_folders()).json()
    all_resources = (await joplin.get_resources()).json()
    resource_folder = 'resources'

    notes_dict = generate_dict_with_all_notes_and_ids(all_notes)
    folders_dict = generate_dict_with_folder_and_ids(all_folders)
    resrouces_types_dict = generate_dict_with_all_resources(all_resources)

    for resource in all_resources:
        response = await download_resource(joplin, resource, resource_folder)

    if not os.path.exists('notes'):
        os.makedirs('notes')

    for note in all_notes:
        file_path = os.path.join("notes", remove_spaces(note['title']))
        try:
            note_body = search_and_replace_joplin_note_links(note['body'], notes_dict)
        except KeyError:
            note_body = search_and_replace_joplin_resource_links(note['body'], resrouces_types_dict, resource_folder)

        with open(f'{file_path}.md','wb') as md_note:
            s = f"""---
title: `{note['title']}`
category: {get_folder_title(note, folders_dict)}
id: {note['id']}
parent_id: {note['parent_id']}
created_at: {note['created_time']}
---

{note_body}
                """
            md_note.write(s.encode("utf-8"))

if __name__ == "__main__":
    cli_options = parse_options()
    
    asyncio.run(
        main(cli_options)
    )