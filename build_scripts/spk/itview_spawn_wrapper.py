#!/usr/bin/env python
import sys
import subprocess

# Configure these globals to control what goes where

# The underlying application to launch
TARGET = "itview"

# The command to run inside the launched environment
COMMAND = "itview"

# Note: you can set all these to empty lists to have where the
# argument will go completely controlled by where the user puts the
# '--' on the command line when they use this wrapper.

# These args always go to spawn, e.g. --versions
SPAWN_FLAGS = ["--versions", "-versions"]
# These args always go to spawn and they will have a single value
# following them, e.g. --appver 42 or --appver=42
SPAWN_ONE_VALUE_ARGS = ["--appver", "-appver"]

# These args always go to the target application, e.g. --always-for-app
APP_FLAGS = ["--always-for-app"]
# These args always go to the target application and they will have
# a single value following them, e.g. --never-for-spawn=42
APP_ONE_VALUE_ARGS = ["--never-for-spawn"]

# This is the function that does the work of splitting up a list of
# command line arguments and deciding where they should go
#
def split_spawn_and_app_args(
    args,
    spawn_flags=None,
    spawn_one_value_args=None,
    app_flags=None,
    app_one_value_args=None,
):
    """Get a list of spawn args and application args from the args and
    sets of arg tokens meant for either spawn or the underlying
    application.

    Returns: two lists, one containing the arguments for spawn, and
    the other containing the argruments for the underlying application.
    """

    # Turn any of the optional args that wasn't given into a list
    # because the rest of this expects them to be lists.
    if spawn_flags is None:
        spawn_flags = []
    if spawn_one_value_args is None:
        spawn_one_value_args = []
    if app_flags is None:
        app_flags = []
    if app_one_value_args is None:
        app_one_value_args = []

    # This needs a few lists and flags to keep track of things
    spawnargs = []
    appargs = []
    put_next_in_spawn = False
    put_next_in_app = False
    before = []
    after = []
    # For the '--' arg
    marker_found = False

    # Spin through the args and categories them (and their values)
    # into for spawn and for the application.
    #
    for arg in args:
        # spawn - for the value after a one value arg
        if put_next_in_spawn:
            spawnargs.append(arg)
            put_next_in_spawn = False
            continue

        # app - for the value after a one value arg
        if put_next_in_app:
            appargs.append(arg)
            put_next_in_app = False
            continue

        # spawn - e.g. wrapper --versions
        if arg in spawn_flags:
            spawnargs.append(arg)
            continue

        # app - e.g. wrapper --versions
        if arg in app_flags:
            appargs.append(arg)
            continue

        # spawn - e.g. wrapper --appver 42
        if arg in spawn_one_value_args:
            spawnargs.append(arg)
            put_next_in_spawn = True
            continue

        # app - e.g. wrapper --appver 42
        if arg in app_one_value_args:
            appargs.append(arg)
            put_next_in_app = True
            continue

        # e.g. wrapper --appver=42
        if "=" in arg:
            part = arg.split("=")
            # spawn
            if part[0] in spawn_one_value_args:
                spawnargs.append(arg)
                continue
            # app
            if part[0] in app_one_value_args:
                appargs.append(arg)
                continue

        # e.g. wrapper --arg1 '--' --argB
        if arg == "--":
            if marker_found:
                # This is for the second and subsequent '--'s.
                after.append(arg)
            else:
                # This is the first '--'. It indicates args before it
                # are spawn and args after it are for the application
                marker_found = True
        else:
            # Normal args are placed in the current list, which is
            # based on whether there's been a '--' among the args
            if marker_found:
                after.append(arg)
            else:
                before.append(arg)

    # Now all the args have been split into lists, work out which list
    # is for spawn and which is for the application.
    #
    if marker_found:
        # '--' was given so "after" is for the application
        appargs.extend(after)
        spawnargs.extend(before)
    else:
        # No '--' given so "before" is for the application
        appargs.extend(before)
        spawnargs.extend(after)

    #print("Debug: spawn args:", spawnargs)
    #print("Debug:   app args:", appargs)

    return spawnargs, appargs


# The main wrapper
#
# Split up the command line arguments. Don't pass the name of this
# program (sys.argv[0]) to the function.
spawnargs, appargs = split_spawn_and_app_args( sys.argv[1:],
                                               SPAWN_FLAGS,
                                               SPAWN_ONE_VALUE_ARGS,
                                               APP_FLAGS,
                                               APP_ONE_VALUE_ARGS
                                              )

# Assemble the command and run it
cmd = ["spawn", "launch"]
cmd.extend(spawnargs)
cmd.append(TARGET)
cmd.append("--")
cmd.append(COMMAND)
cmd.extend(appargs)

#print("Debug: about to run:", " ".join(cmd))
result = subprocess.call(cmd)
sys.exit(result)
