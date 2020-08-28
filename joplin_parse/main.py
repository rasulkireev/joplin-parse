import os
import asyncio
import argparse
from joplin_api import JoplinApi
from joplin_parse.utils import (
    remove_spaces,
    generate_dict_with_folder_and_ids,
    generate_dict_with_all_notes_and_ids,
    generate_dict_with_all_resources,
    search_and_replace_joplin_note_links,
    search_and_replace_joplin_resource_links,
    get_folder_title,
    download_resource,
    choose_folders_to_parse,
    generate_note,
    generate_dict_with_all_resources_filenames,
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

    all_notes = (await joplin.get_notes()).json()
    all_folders = (await joplin.get_folders()).json()
    all_resources = (await joplin.get_resources()).json()

    notes_folder = "notes"
    resource_folder = "resources"

    response = input("Do you want to parse all folders? [y/n]")
    if response == "n":
        all_folders = choose_folders_to_parse(all_folders)
    elif response == "y":
        pass
    else:
        print("Incorrect response")

    folders_dict = generate_dict_with_folder_and_ids(all_folders)
    notes_dict = generate_dict_with_all_notes_and_ids(all_notes)

    resources_types_dict = generate_dict_with_all_resources(all_resources)
    resources_names_dict = generate_dict_with_all_resources_filenames(all_resources)

    for resource in all_resources:
        response = await download_resource(
            joplin, resource, os.path.join(notes_folder, resource_folder)
        )

    if not os.path.exists(notes_folder):
        os.makedirs(notes_folder)

    for note in all_notes:
        file_path = os.path.join(notes_folder, remove_spaces(note["title"]))
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

        if note["parent_id"] in folders_dict:
            note["category"] = get_folder_title(note, folders_dict)
            generate_note(file_path, note)
        else:
            continue


if __name__ == "__main__":
    cli_options = parse_options()

    asyncio.run(main(cli_options))
