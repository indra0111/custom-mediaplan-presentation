#!/bin/bash

source .venv/bin/activate
uvicorn src.genai_mediaplan.api:app --host 0.0.0.0 --port 8001 --reload