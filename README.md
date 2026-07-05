# Kandidaten Beheer

Eerste MVP in Streamlit met Supabase.

## Projectstructuur

```text
.
+-- app.py
+-- database/
|   +-- schema.sql
|   +-- 002_update_offers_targetlijst.sql
+-- requirements.txt
+-- .streamlit/
    +-- secrets.example.toml
```

## Starten

1. Maak een Supabase-project aan.
2. Nieuwe database: voer `database/schema.sql` uit in de SQL editor van Supabase.
3. Bestaande MVP-database: voer daarna `database/002_update_offers_targetlijst.sql` uit.
4. Kopieer `.streamlit/secrets.example.toml` naar `.streamlit/secrets.toml`.
5. Vul `SUPABASE_URL` en `SUPABASE_KEY` in.
6. Installeer de dependencies:

```powershell
pip install -r requirements.txt
```

7. Start de app:

```powershell
streamlit run app.py
```
