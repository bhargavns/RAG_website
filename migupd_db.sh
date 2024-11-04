#!/bin/bash
cd backend || python app.py

# Initialize the migration repository (run this only once)
if [ "$2" == "init" ]; then
    flask db init
fi

# Generate a new migration script
flask db migrate -m "$1"

# Apply the migration to the database
flask db upgrade