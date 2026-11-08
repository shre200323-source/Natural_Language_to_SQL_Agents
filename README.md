# Natural Language to SQL Agent

## Run (from the `nl_sql_agent` folder)

```bat
pip install -r ..\requirements.txt
ollama pull gemma3:1b
uvicorn app.main:app --reload              # terminal 1 - API on http://localhost:8000
streamlit run frontend\streamlit_app.py    # terminal 2 - UI on http://localhost:8501
```

## Folder structure

```
nl_sql_agent/
├── app/
│   ├── main.py                FastAPI: POST /ask, GET /health
│   └── graph/                 LangGraph: state.py, nodes.py, builder.py
├── Configuration/config.py    model, temperature, seed, context size, attempts, DB path
├── functions/functions.py     SQL validation, execution, SQL cleanup, schema reading
├── prompts/
│   ├── generate_node.py       prompt for generating SQL
│   └── format_answer_node.py  prompt for writing the answer
├── frontend/streamlit_app.py  Streamlit UI
├── data/                      sales.db
├── scripts/__init__db.py      creates sales.db
└── tests/test_db.py
```
