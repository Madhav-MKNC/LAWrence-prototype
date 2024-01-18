# Project LAWrence

Swiss legal memo generation tool with UI, LLM orchestration, and flexible data model for summarization, title generation, and question extraction.

Steps to run the system on local.

```
cd ./uc-02
touch .env
```

Add the following creds inside .env file inside the the uc-02 folder and save it.

```
OPENAI_API_KEY=
ENDPOINT=
COSMOS_DB_KEY=
DATABASE_NAME=
CONTAINER_NAME=
```

```
python app.py
```

