run:
	rm -f tests/db.sqlite3
	uv pip install -e .
	uv run python tests/manage.py migrate --noinput
	uv run python tests/manage.py runserver
