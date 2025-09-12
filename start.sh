#!/bin/bash
cd /opt/render/project
if [ -f "src/simple_main.py" ]; then
    echo "Found simple_main.py in src/"
    python src/simple_main.py
elif [ -f "simple_main.py" ]; then
    echo "Found simple_main.py in root"
    python simple_main.py
else
    echo "simple_main.py not found, listing directory:"
    ls -la
    echo "Contents of src/:"
    ls -la src/
    exit 1
fi