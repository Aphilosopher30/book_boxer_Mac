#!/bin/bash

# Pipeline Runner
# Runs three scripts in sequence, stopping if any script fails.

set -e  # Exit immediately if any command fails

echo "========================================="
echo " Starting Pipeline"
echo "========================================="

echo ""
echo "[1/4] Running export_collections.py..."
python export_collections.py
echo "      Done."

echo ""
echo "[2/4] Running Tables/Combine_CSVS.py..."
python Tables/combine_csvs.py ./Tables/Raw_Downloads/*.csv --output Tables/all_collections.csv
echo "      Done."

echo ""
echo "[3/4] Running Tables/add_photo_collumn.py..."
python Tables/add_photo_column.py --csv Tables/all_collections.csv  --folder ./Tables/photos
echo "      Done."

echo ""
echo "[4/4] Deleting all raw downloads..."
./Tables/delete_files.sh -y ./Tables/Raw_Downloads
echo "      Done."


echo ""
echo "========================================="
echo " Pipeline complete!"
echo "========================================="
