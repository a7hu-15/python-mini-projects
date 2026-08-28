# 🔄 CLI JSON / XML Converter & Formatter

A multi-format data structure converter for transforming JSON documents to XML and vice versa with custom indentation options.

## Features
- Convert JSON to formatted XML trees
- Convert XML structures back to JSON dictionaries
- Re-indent and validate JSON data structures

## Usage

```bash
# Convert JSON to XML
python json_converter.py data.json --to-xml -o data.xml

# Convert XML back to formatted JSON
python json_converter.py data.xml --from-xml --indent 4
```

## Running Tests

```bash
python3 -m unittest test_json_converter.py
```
