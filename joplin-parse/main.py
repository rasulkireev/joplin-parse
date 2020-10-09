import os
import re
import json
import asyncio
from joplin_api import JoplinApi

TOKEN ="5ba2569164f8f0fdae8cfca2552094e994099b8868e2c1a70211b4748cff006dafc92f73f0822425a0df537969554bfc8a72496f6a08042c56272abc2f508f03"
joplin = JoplinApi(token=TOKEN)
current_dir = os.getcwd()

async def ping_me(joplin):
    ping = await joplin.ping()
    return ping

async def get_my_notes(joplin):
    notes = await joplin.get_notes()
    return notes

async def get_my_folders(joplin):
    notes = await joplin.get_folders()
    return notes

async def main():
    notes = await get_my_notes(joplin)
    folders = await get_my_folders(joplin)

    folders_json = folders.json()
    notes_json = notes.json()
    resource_folders = folders_json[2]["children"]

    for i in range(len(resource_folders)):
        resource = resource_folders[i]
        resource_title = resource["title"]
        resource_id = resource["id"]

        folder_path = os.path.join(current_dir, "resources", resource_title)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    for folder in resource_folders:
        folder_path = os.path.join(current_dir, "resources", folder["title"])
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
    asyncio.run(main())