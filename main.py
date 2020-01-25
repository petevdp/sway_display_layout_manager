#!/usr/bin/python

import subprocess
import os
import json
import argparse


CONFIG_DIR = "/home/pete/.config/screen_layouts"
SHELL_PATH = "/usr/bin/sh"


def save_config(filename):
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

    if not os.path.exists(script_path):
        raise Exception("configuration {config_name} does not exist")

    os.system(script_path + " && echo \"success\"")


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='save and set sway output configurations')

    parser.add_argument('-c', type=str, metavar='NAME',
                        help="choose a configuration")

    parser.add_argument('-s',
                        metavar='NAME',
                        type=str,
                        help="save the current screen layout configuration"
                        )

    args = parser.parse_args()

    # get the args being invoced
    arg_list = [a for a in vars(args).items() if a[1] != None]

    if len(arg_list) == 0:
        raise "please supply an argument (-h for options)"

    if len(arg_list) > 1:
        raise "too many arguments!"

    arg_name, arg = arg_list[0]

    if arg_name == 's':
        filename = arg
        save_config(filename)
        print(f"current configuration saved as {filename}")
    elif arg_name == 'c':
        config_name = arg
        run_config(config_name)
    else:
        raise Exception(f"invalid flag {arg_name}")
