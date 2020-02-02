#!/usr/bin/python

import subprocess
import os
import sys
import json
import argparse


CONFIG_DIR = "/home/pete/.config/screen_layouts"
SHELL_PATH = "/usr/bin/sh"


def list_configs():
    configs = os.listdir(CONFIG_DIR)
    for config in configs:
        print(config)


def save_config(filename):
    file_path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(file_path):
        return write_config(filename)

    while True:
        overwrite_response = input(
            f"A configuration with name {filename} already exists. overwrite?(y/n): ")

        if overwrite_response in ['y', 'Y']:
            return write_config(filename)

        if overwrite_response in ['n', 'N']:
            new_filename = input("new filename: ")
            if new_filename == filename:
                continue
            return write_config(new_filename)


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
    print(f"current configuration saved as {filename}")


def run_config(config_name):
    script_path = os.path.join(CONFIG_DIR, config_name)

    if not os.path.exists(script_path):
        raise Exception("configuration {config_name} does not exist")

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
