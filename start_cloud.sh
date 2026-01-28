#!/bin/bash

# Initialize Data
echo "Initializing Store A..."
python3 mock-server/import_csv.py --products_db_path=store_a.db --transactions_db_path=store_a_trans.db --data_dir=mock-server/data/store_a

echo "Initializing Store B..."
python3 mock-server/import_csv.py --products_db_path=store_b.db --transactions_db_path=store_b_trans.db --data_dir=mock-server/data/store_b

# Start processes in background
echo "Starting Store A (8182)..."
python3 mock-server/server.py --products_db_path=store_a.db --transactions_db_path=store_a_trans.db --port=8182 > store_a.log 2>&1 &

echo "Starting Store B (8183)..."
python3 mock-server/server.py --products_db_path=store_b.db --transactions_db_path=store_b_trans.db --port=8183 > store_b.log 2>&1 &

echo "Starting Recipe Agent (Monolith with Frontend)..."
# Render sets PORT environment variable. If not set, default to 10000 (Render default) or 8000.
# We bind to 0.0.0.0 to be accessible externally.
uvicorn recipe-agent.main:app --host 0.0.0.0 --port ${PORT:-10000}

