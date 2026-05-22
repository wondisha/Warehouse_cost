# Warehouse Cost - Snowflake Intelligence Agent

A Streamlit in Snowflake app that uses **Cortex Analyst** to answer natural language questions about warehouse efficiency and credit consumption.

## What It Does

This app provides a chat interface where users can ask questions like:
- "Which warehouse consumes the most credits?"
- "Show me warehouse efficiency metrics"
- "What are the peak hourly credits by warehouse?"

Cortex Analyst translates natural language into SQL queries against a semantic model, executes them, and displays results — all within a conversational UI.

## Architecture

- **Frontend:** Streamlit in Snowflake (SiS)
- **AI Engine:** Cortex Analyst (`/api/v2/cortex/analyst/message`)
- **Auth:** Internal session token (no external access integration needed)
- **Data:** `DBADMIN.PUBLIC.FINOPS_WH_EFFICIENCY` view

## Files

| File | Description |
|------|-------------|
| `streamlit_app.py` | Main Streamlit app with chat UI and Cortex Analyst integration |
| `finops_model.yaml` | Semantic model defining dimensions and measures for the cost data |

## Deployment Steps

### 1. Create the Stage

```sql
CREATE STAGE IF NOT EXISTS DBADMIN.ASSETS.MODEL_STAGE;
```

### 2. Upload the Semantic Model

Upload using SnowSQL (CLI) from your local machine:

```bash
snowsql -q "PUT file://finops_model.yaml @DBADMIN.ASSETS.MODEL_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
```

### 3. Ensure the View Exists

```sql
SELECT * FROM DBADMIN.PUBLIC.FINOPS_WH_EFFICIENCY LIMIT 1;
```

### 4. Deploy the Streamlit App

1. Open Snowsight → Workspaces
2. Create a new Streamlit project
3. Paste `streamlit_app.py` contents
4. Run the app

## Semantic Model

The `finops_model.yaml` exposes:

| Type | Name | Description |
|------|------|-------------|
| Dimension | `warehouse_name` | Name of the virtual warehouse |
| Measure | `avg_hourly_credits` | Average credits consumed per hour |
| Measure | `hours_active` | Hours the warehouse was active |
| Measure | `peak_hourly_credits` | Peak credits in a single hour |

## Key Implementation Details

- Uses `requests.post()` with `session.connection._rest.token` for authenticated API calls
- Enforces strict user/analyst role alternation in message history (API requirement)
- Multi-turn conversation support with session state
- Displays SQL queries in expandable sections with live results
