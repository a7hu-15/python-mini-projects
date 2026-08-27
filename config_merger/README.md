# CLI JSON & Config Merger & Diff Tool

A Python utility for deep-merging multiple JSON configuration files, processing environment variable placeholders, and computing key-by-key structural differences.

## Features
- **Deep Dictionary Merge**: Recursively combines nested JSON key trees in cascading priority order.
- **Environment Variable Substitution**: Expands placeholders like `${ENV_VAR:default_value}` within string properties.
- **Structural Diff Engine**: Identifies added `[+]`, removed `[-]`, and modified `[~]` key paths between two configurations.

## Usage

### Interactive Demo
```bash
python config_merger.py
```

### Cascading Configuration Merge
```bash
python config_merger.py base.json environment.json local.json -o final_config.json
```

### Compare Structural Differences
```bash
python config_merger.py --diff dev_config.json prod_config.json
```

### Run Unit Tests
```bash
python -m unittest test_config_merger.py
```
