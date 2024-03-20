**Active virtual environment:**
`source venv/bin/activate`

**Run fastapi server:**
`uvicorn src.main:app --reload`

**Generate alembic revison scripts to update DB schema:**
`alembic revision --autogenerate -m "some comment"`

**Update DB schema:**
`alembic upgrade head`

**Print project tree:**
`tree -L 3`

**List libraries:**
`pip list`

**Generate requirements.txt:**
`pip freeze > requirements.txt`

**Tailwind auto-rebuild:**
`tailwindcss -i ./static/css/tw.css -o ./static/css/tailwind.css --watch`