.PHONY: install install-dev install-live install-real install-gcp install-llm app test evaluate evaluate-live shadow ingest docker audit verify clean

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements-dev.txt

install-live:
	python -m pip install -r requirements-live.txt

install-real:
	python -m pip install -r requirements-real.txt

install-gcp:
	python -m pip install -r requirements-gcp.txt

install-llm:
	python -m pip install -r requirements-llm.txt

app:
	streamlit run app.py

test:
	pytest -q

evaluate:
	python evaluation/run_retrieval_evaluation.py
	python evaluation/run_answer_evaluation.py

evaluate-live:
	python evaluation/run_live_llm_evaluation.py

shadow:
	python scripts/run_shadow_mode.py

ingest:
	python -m src.pennantiq.ingestion

docker:
	docker compose up --build

audit:
	python scripts/audit_repository.py

verify:
	python -m compileall -q src app.py evaluation scripts tests
	python scripts/audit_repository.py
	python -m src.pennantiq.ingestion
	pytest -q
	python evaluation/run_retrieval_evaluation.py
	python evaluation/run_answer_evaluation.py
	python scripts/run_shadow_mode.py

clean:
	rm -rf .pytest_cache __pycache__ data/runtime/* evaluation/results/*
