#!/usr/bin/env python3

# Third Party
from pyannotate_runtime import collect_types

# First Party
from seotool import cli

if __name__ == "__main__":
    collect_types.init_types_collection()
    with collect_types.collect():
        cli.main()
    collect_types.dump_stats("type_info.json")
