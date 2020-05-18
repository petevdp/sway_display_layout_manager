#!/usr/bin/python

import subprocess
import os
import sys
import json
import argparse


CONFIG_DIR = os.path.join(os.environ['HOME'], ".config", "screen_layouts")
SHELL_PATH = "/usr/bin/sh"
DATA_FILE = os.path.join(CONFIG_DIR, "data.json")

def list_configs():
    configs = os.listdir(CONFIG_DIR)
    for config in configs:
        print(config)


def save_config(filename):
    file_path = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(file_path):
        while True:
            overwrite_response = input(
                f"A configuration with name {filename} already exists. overwrite?(y/n): ")

            if overwrite_response.lower == 'y':
                return write_config(filename)

            if overwrite_response.lower == 'n':
                new_filename = input("new filename: ")
                if new_filename == filename:
                    continue
                break

    print(f"current configuration saved as {filename}")
    return write_config(filename)

def save_config_name_as_current(config_name):
    config_path = os.path.join(CONFIG_DIR, config_name)
    if not os.path.exists(config_path):
        raise Exception(f'tried to save {config_name} as current, but {config_path} does not exist')

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            curr_data = json.loads(f.read())
    else:
        curr_data = {}

    curr_data["current_config"] = config_name

    with open(DATA_FILE, "w+") as f:
        f.write(json.dumps(curr_data))

def write_config(filename):
    commands = gen_output_pos_config_from_current_position()
    command_lines = '\n'.join(commands)

    script_contents = \
        f"#!{SHELL_PATH}\n" \
        + f"{command_lines}\n"

    file_path = os.path.join(CONFIG_DIR, filename)

    with open(file_path, 'w') as f:
        f.write(script_contents)

    os.system(f'chmod +x {file_path}')


def run_config(config_name):
    script_path = os.path.join(CONFIG_DIR, config_name)

    if config_name == "current":
        try:
            with open(DATA_FILE, "r") as f:
                data = json.loads(f.read())
            if 'current_config' in data:
                current_script_path = os.path.join(CONFIG_DIR, data['current_config'])
                if not os.path.exists(current_script_path):
                    raise Exception(f'Configuration saved as current({current_script_path}) does not exist')
                script_path = current_script_path
            else:
                raise Exception("No current config")
        except FileNotFoundError:
            raise Exception("No current config")
    else:
        if not os.path.exists(script_path):
            raise Exception("configuration {config_name} does not exist")
        save_config_name_as_current(config_name)

    os.system(script_path + " && echo \"success\"")


def delete_config(config_name):
    script_path = os.path.join(CONFIG_DIR, config_name)

    if not os.path.exists(script_path):
        raise Exception("configuration {config_name} does not exist")

    os.remove(script_path)
    print("success")


def gen_output_pos_config_from_current_position():
    outputs = get_sway_outputs()
    return [get_pos_config_command_for_output(output) for output in outputs]


def get_pos_config_command_for_output(output):
    rect = output['rect']
    name = output['name']

    return f"swaymsg output {name} position {rect['x']} {rect['y']}"


def get_sway_outputs():
    output_str = subprocess.check_output(['swaymsg', '-t', 'get_outputs'])
    return json.loads(output_str)


def main():
    parser = argparse.ArgumentParser(
        description='Save and set sway output configurations. Only provide one argument.')

    parser.add_argument('-s',
                        metavar='NAME',
                        type=str,
                        help="save the current screen layout configuration"
                        )
    parser.add_argument('-c', type=str, metavar='NAME',
                        help="choose a configuration")
    parser.add_argument('-d', type=str, metavar='NAME')
    parser.add_argument('-l', action='store_true', help="list current configs")

    args = parser.parse_args()

    # get the args being invoced
    arg_list = [a for a in vars(args).items() if a[1]]

    if len(arg_list) == 0:
        parser.print_help()
        sys.exit(1)

    if len(arg_list) > 1:
        parser.print_help()
        sys.exit(1)

    arg_name, arg = arg_list[0]

    if arg_name == 's':
        filename = arg
        save_config(filename)
    elif arg_name == 'c':
        config_name = arg
        run_config(config_name)
    elif arg_name == 'd':
        config_name = arg
        delete_config(config_name)
    elif arg_name == 'l':
        list_configs()
    else:
        raise Exception(f"invalid flag {arg_name}")


if __name__ == "__main__":
    main()
