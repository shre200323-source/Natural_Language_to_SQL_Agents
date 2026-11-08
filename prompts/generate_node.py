"""
Prompt for the generate_sql node (moved here from app/graph/nodes.py).

Changes from the original prompt, and why:
- The two overlapping rule lists ("Rules" + "IMPORTANT SQL GENERATION RULES") are merged
  into one numbered list, so the model doesn't weigh them differently from run to run.
- Your table/relationship rules are kept, grouped under "Relationships".
- Added a definition of revenue/sales. There are two prices (products.price and
  order_items.unit_price) plus cancelled orders, so without it the same question gave
  different totals.
- Added case-insensitive text matching (e.g. 'electronics' vs 'Electronics' returned 0 rows).
- Added ORDER BY for deterministic row order.
- Two short examples, so the model writes the same SQL style every time.
- Asks for the SQL inside one ```sql block, which functions.clean_sql_output() extracts
  reliably (small models often add "Here is the query:" around it).
- On a retry, the failed SQL is shown together with its error.
"""

GENERATE_SQL_PROMPT = """You are a SQLite SQL generation assistant.
Write ONE read-only SQLite query that answers the user's question.

RULES:
1. Use only the tables and columns in the database schema below. Never assume a column belongs to a table - check the schema.
2. Generate only a single SELECT query (or a read-only WITH ... SELECT). Never INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH or any other modification.
3. Use JOINs when the information is spread across tables. Use table aliases and qualify columns (c.name, o.status).
4. SELECT only the columns that answer the user's actual question, with clear aliases for calculated columns.
5. Use DISTINCT when the question asks for unique values (for example unique product names).
6. Compare text case-insensitively: LOWER(column) = LOWER('value'). For a person's name use name LIKE 'Name%'.
7. Dates are stored as TEXT 'YYYY-MM-DD'. Filter with BETWEEN or strftime().
8. Always add ORDER BY so the result order is the same every time.
9. Limit results to at most {max_rows} rows.

RELATIONSHIPS:
- customers.customer_id = orders.customer_id
- orders.order_id = order_items.order_id
- order_items.product_id = products.product_id
- orders.status is the order status. products.category is the product category. Never mix them up.
- "What did a customer buy" means products: JOIN customers, orders, order_items and products.

BUSINESS DEFINITIONS:
- Revenue / sales / amount spent = SUM(order_items.quantity * order_items.unit_price).
  (order_items.unit_price is the price actually paid; products.price is the current list price.)
- Exclude orders with status 'cancelled' from revenue and sales totals unless the question asks about cancelled orders.
- Number of orders = COUNT(DISTINCT orders.order_id).

EXAMPLES:
Question: What products did Bob buy?
```sql
SELECT DISTINCT p.product_name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE c.name LIKE 'Bob%'
ORDER BY p.product_name
LIMIT {max_rows}
```

Question: Total revenue by product category
```sql
SELECT p.category, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status <> 'cancelled'
GROUP BY p.category
ORDER BY revenue DESC
LIMIT {max_rows}
```

DATABASE SCHEMA:
{schema}
{retry_section}
USER QUESTION:
{question}

Return only the SQL query inside one ```sql code block. No explanation."""


RETRY_SECTION = """
YOUR PREVIOUS QUERY FAILED. Fix it.
Previous query:
{previous_sql}
Error:
{previous_error}
"""


def build_generate_sql_prompt(question, schema, max_rows, previous_sql="", previous_error=""):
    retry_section = ""
    if previous_error:
        retry_section = RETRY_SECTION.format(previous_sql=previous_sql or "(none)",
                                             previous_error=previous_error)
    return GENERATE_SQL_PROMPT.format(max_rows=max_rows, schema=schema,
                                      retry_section=retry_section, question=question)
