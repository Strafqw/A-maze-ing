import json


def read_confs(confs_file: str = "config.txt"):
    try:
        config = {}

        int_measures = ["WIDTH", "HEIGHT", "ENTRY", "EXIT"]
        with open(confs_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    except Exception as e:
        raise type(e) (f"Error on read_confs | {e}")

    print(json.dumps(config, indent=2))

read_confs()
