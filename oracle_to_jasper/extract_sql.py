from lxml import etree
import sqlparse
import json
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {"prompt": prompt, "max_tokens": 500}
    for attempt in range(3):
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return json.loads(response.json().get("choices")[0].get("text"))
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"LLM API error (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise Exception("LLM API failed after retries")

def extract_and_validate_sql(rdf_file, output_file, target_db="MySQL"):
    try:
        tree = etree.parse(rdf_file)
        queries = tree.xpath("//query/text()")
        validated_queries = []

        for query in queries:
            prompt = f"""
            **Persona**: You are a Senior Digital Transformation Engineer with expertise in SQL and JasperReports integration.

            **Task**: Validate and rewrite an Oracle RDF SQL query for compatibility with a target database and generate a JasperReports JDBC data source configuration.

            **Input**:
            - SQL query:
            ```sql
            {query}
            ```
            - Target database: {target_db}
            - Context: Oracle RDF reports embed SQL in `<query>` elements. JasperReports uses `<queryString>` or JDBC data sources.

            **Instructions**:
            1. Validate the SQL query for syntax and {target_db} compatibility.
            2. Rewrite the query if needed (e.g., replace `:dept` with `?` for {target_db}).
            3. Generate a JasperReports JDBC data source configuration XML for {target_db}.
            4. Ensure the query is compatible with `<queryString language="SQL">`.
            5. Provide comments explaining changes.
            6. Return a JSON object with:
               - `validated_query`: The rewritten SQL query.
               - `jdbc_config`: The JDBC configuration XML.

            **Expected Output**:
            ```json
            {{
              "validated_query": "SELECT name, age FROM employees WHERE dept = ?",
              "jdbc_config": "<dataSource name=\\"myDataSource\\" class=\\"com.mysql.jdbc.jdbc2.optional.MysqlDataSource\\" url=\\"jdbc:mysql://localhost:3306/db\\" user=\\"user\\" password=\\"pass\\"/>"
            }}
            ```

            **Constraints**:
            - Ensure {target_db} compatibility.
            - Handle Oracle-specific bind variables (e.g., `:dept`).
            - Keep the JDBC config compatible with JasperReports Server 6.x.
            """
            response = call_llm(prompt)
            validated_query = response.get("validated_query", query)
            with open(f"jdbc_config_{os.path.basename(rdf_file)}.xml", "w") as f:
                f.write(response.get("jdbc_config", ""))
            formatted_query = sqlparse.format(validated_query, reindent=True, keyword_case="upper")
            validated_queries.append(formatted_query)

        with open(output_file, "w") as f:
            for i, query in enumerate(validated_queries, 1):
                f.write(f"Query {i}:\n{query}\n\n")
        print(f"Extracted {len(validated_queries)} queries to {output_file}")
        return validated_queries
    except Exception as e:
        print(f"Error processing {rdf_file}: {e}")
        return []

if __name__ == "__main__":
    extract_and_validate_sql("report.rdf", "queries.sql", "MySQL")