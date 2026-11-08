"""
Prompt for the format_answer node (moved here from app/graph/nodes.py).

Changes: same rules as your original, plus "use the exact numbers", a length limit,
and no SQL talk in the answer. The result is passed as a readable table instead of
a raw Python dict string, which small models misread.
"""

FORMAT_ANSWER_PROMPT = """Answer the user's question using only the SQL results below.

RULES:
- Do not invent values or claim facts that the results do not show.
- Use the exact numbers from the results, with thousands separators (60000 -> 60,000).
- If the results are insufficient, explain that clearly.
- Keep it short: one or two sentences, or a short bullet list if there are several rows.
- Do not mention SQL, tables or queries in the answer.

QUESTION:
{question}

QUERY RESULTS ({row_count} rows):
{results_table}

ANSWER:"""


def build_format_answer_prompt(question, columns, rows, max_rows_in_prompt=30):
    lines = [" | ".join(str(c) for c in columns)]
    lines += [" | ".join(str(v) for v in row) for row in rows[:max_rows_in_prompt]]
    if len(rows) > max_rows_in_prompt:
        lines.append(f"... ({len(rows) - max_rows_in_prompt} more rows not shown)")
    return FORMAT_ANSWER_PROMPT.format(question=question, row_count=len(rows),
                                       results_table="\n".join(lines))
