from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


class ConfigError(Exception):
    """Raised when the config file is missing, malformed, or invalid."""


def parse_config(path: str) -> Config:
    # 1. read file (context manager, catch FileNotFoundError)
    raw: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as f:
            for lineno, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if '=' not in line:
                    raise ConfigError(f"line {lineno}: expected "
                                      f"KEY=VALUE, got {line!r}")
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    raise ConfigError(f"line {lineno}: empty key")
                if key in raw:
                    raise ConfigError(
                        f"line {lineno}: duplicate key {key!r}"
                    )
                raw[key] = value
    except OSError as e:
        raise ConfigError(f"cannot read config file: {path}: {e}") from e
    required = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    missing = required - raw.keys()
    if missing:
        raise ConfigError(f"missing required keys: {sorted(missing)}")

    def parse_int(raw_value: str, key: str) -> int:
        try:
            return int(raw_value)
        except ValueError as e:
            raise ConfigError(
                f"{key}: expected integer, got {raw_value!r}"
                ) from e

    def parse_bool(raw_value: str, key: str) -> bool:
        if raw_value.lower() in ("true", "1", "yes"):
            return True
        if raw_value.lower() in ("false", "0", "no"):
            return False
        raise ConfigError(f"{key}: expected boolean, got {raw_value!r}")

    def parse_coords(raw_value: str, key: str) -> tuple[int, int]:
        parts = raw_value.split(",")
        if len(parts) != 2:
            raise ConfigError(f"{key}: expected 'x,y', got {raw_value!r}")
        try:
            x = int(parts[0].strip())
            y = int(parts[1].strip())
        except ValueError as e:
            raise ConfigError(f"{key}: coordinates must be integers, "
                              f"got {raw_value!r}") from e
        return (x, y)
    width = parse_int(raw["WIDTH"], "WIDTH")
    height = parse_int(raw["HEIGHT"], "HEIGHT")
    entry = parse_coords(raw["ENTRY"], "ENTRY")
    exitcoor = parse_coords(raw["EXIT"], "EXIT")
    output_file = raw["OUTPUT_FILE"]
    perfect = parse_bool(raw["PERFECT"], "PERFECT")
    seed = parse_int(raw["SEED"], "SEED") if "SEED" in raw else None
    if width <= 0:
        raise ConfigError(f"WIDTH must be > 0, got {width}")
    if height <= 0:
        raise ConfigError(f"HEIGHT must be > 0, got {height}")
    ex, ey = entry
    if not (0 <= ex < width and 0 <= ey < height):
        raise ConfigError(
            f"ENTRY {entry} is outside maze bounds {width}x{height}"
        )
    ex1, ey2 = exitcoor
    if not (0 <= ex1 < width and 0 <= ey2 < height):
        raise ConfigError(
            f"EXIT {exitcoor} is outside maze bounds {width}x{height}"
        )
    if entry == exitcoor:
        raise ConfigError("ENTRY and EXIT must differ")
    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exitcoor,
        output_file=output_file,
        perfect=perfect,
        seed=seed
    )


if __name__ == "__main__":
    cfg = parse_config("config.txt")
    print(cfg)
