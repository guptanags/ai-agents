from lxml import etree
import sqlparse
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.post(api_url, json={"prompt": prompt, "max_tokens": 500})
    return response.json().get("choices")[0].get("text")

def extract_and_validate_sql(rdf_file, output_file, target_db="MySQL"):
    try:
        tree = etree.parse(rdf_file)
        queries = tree.xpath("//query/text()")
        validated_queries = []

        for query in queries:
            # LLM prompt for SQL validation and rewriting
            prompt = f"""
            Given the SQL query:
            {query}
            And the target database: {target_db}
            1. Validate the query syntax.
            2. Rewrite the query if needed for {target_db} compatibility.
            3. Return the rewritten query or confirm it is valid.
            """
            validated_query = call_llm(prompt).strip()
            if "invalid" in validated_query.lower():
                print(f"Warning: Invalid query in {rdf_file}: {query}")
                continue
            formatted_query = sqlparse.format(validated_query, reindent=True, keyword_case="upper")
            validated_queries.append(formatted_query)

        # Save queries
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