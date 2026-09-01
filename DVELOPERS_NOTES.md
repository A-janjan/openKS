connect to db :

`$ docker exec -it $(docker ps -qf "name=postgres") psql -U knowledge -d knowledge`

delete info from db:

```
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS relationships CASCADE;  -- has FK to document_chunks
DROP TABLE IF EXISTS entities CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;
```

init db(create schemas):

`python -m scripts.init_db`



feed data to db:

`python -m run_ingestion data/`