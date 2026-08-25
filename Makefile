.PHONY: install run test clean

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	python -m unittest test_resume_analyzer.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf uploads/*
