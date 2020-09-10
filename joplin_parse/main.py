import os
import asyncio
import argparse

from joplin_api import JoplinApi
from joplin_parse.utils import (
    remove_spaces,
    generate_dict_with_all_notes_and_ids,
    generate_dict_with_all_resources,
    search_and_replace_joplin_note_links,
    search_and_replace_joplin_resource_links,
    download_resource,
    choose_folders_to_parse,
    generate_note,
    generate_dict_with_all_resources_filenames,
    create_folders,
)

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

    # Get all notes, folders and resources info.
    all_folders = (await joplin.get_folders()).json()
    all_notes = (await joplin.get_notes()).json()
    folder_id_paths = {}
    note_to_folder_ids_dict = {}

    # Set default locations for generated files
    notes_folder = "notes"
    resource_folder = "resources"

    # Give the user an option to parse all the notebooks or a selection.
    # Rasul TODO: allow to choose multiple notebooks.
    response = input("Do you want to parse all notebooks? [y/n]")
    if response == "n":
        all_folders = choose_folders_to_parse(all_folders)
    elif response == "y":
        pass
    else:
        print("Incorrect response")

    # Generate folders for chosen notebooks
    for folder in all_folders:
        create_folders(folder, notes_folder, folder_id_paths)

    # Generate a dictionary with notes ids as keys and folder ids as values
    for k in folder_id_paths:
        notes = (await joplin.get_folders_notes(k)).json()
        for note in notes:
            note_to_folder_ids_dict[note["id"]] = k

    # Create a new list of notes that appear in selected folders only
    filtered_all_notes = []
    for note in all_notes:
        if note["id"] in note_to_folder_ids_dict:
            filtered_all_notes.append(note)

    # Get a dictionary with note titles and ids
    notes_dict = generate_dict_with_all_notes_and_ids(filtered_all_notes)

    for note in filtered_all_notes:
        all_resources = []
        resources = (await joplin.get_notes_resources(note["id"])).json()

        for resource in resources:
            all_resources.append(resource)
            response = await download_resource(
                joplin, resource, os.path.join(notes_folder, resource_folder)
            )

    resources_types_dict = generate_dict_with_all_resources(all_resources)
    resources_names_dict = generate_dict_with_all_resources_filenames(all_resources)

    for note in filtered_all_notes:
        folder_path = folder_id_paths[note_to_folder_ids_dict[note["id"]]]
        file_path = os.path.join(folder_path, remove_spaces(note["title"]))
        try:
            note["body"] = search_and_replace_joplin_note_links(
                note["body"], notes_dict
            )
        except KeyError:
            note["body"] = search_and_replace_joplin_resource_links(
                note["body"],
                resources_types_dict,
                resources_names_dict,
                resource_folder,
            )

        note["category"] = os.path.basename(os.path.normpath(folder_path))
        generate_note(file_path, note)


if __name__ == "__main__":
    cli_options = parse_options()

    asyncio.run(main(cli_options))
