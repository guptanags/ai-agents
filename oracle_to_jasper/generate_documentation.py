import jinja2
import json
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {"prompt": prompt, "max_tokens": 2000}
    for attempt in range(3):
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get("choices")[0].get("text")
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"LLM API error (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise Exception("LLM API failed after retries")

def generate_documentation(mapping_file, output_file):
    try:
        with open(mapping_file) as f:
            mapping = json.load(f)

        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer with expertise in technical documentation for report migration.

        **Task**: Generate a Markdown documentation file for migrating Oracle RDF reports to JasperReports.

        **Input**:
        - Mapping schema:
        ```json
        {json.dumps(mapping, indent=2)}
        ```
        - Context: The migration involves Python scripts (`inventory_rdf.py`, `convert_rdf_to_jrxml.py`, etc.) to automate RDF to JRXML conversion.

        **Instructions**:
        1. Generate a Markdown file with:
           - **Overview**: Purpose and scope of the migration.
           - **Process Description**: Steps (inventory, mapping, conversion, validation, deployment).
           - **Mapping Schema**: Explanation of key mappings with examples.
           - **Script Instructions**: How to run each script with example commands.
           - **Troubleshooting Tips**: Common issues (e.g., XML parsing errors, SQL compatibility) and solutions.
        2. Use clear, concise language suitable for technical users.
        3. Include code blocks for script examples and JSON snippets.
        4. Ensure the document is well-structured with headings and bullet points.

        **Expected Output**:
        A Markdown string, e.g.:
        ```markdown
        # Oracle RDF to JasperReports Migration

        ## Overview
        This document describes the automated migration of Oracle RDF reports to JasperReports.

        ## Process
        1. **Inventory**: Run `inventory_rdf.py` to catalog reports.
        2. **Conversion**: Run `convert_rdf_to_jrxml.py` to generate JRXML files.
        ...

        ## Mapping Schema
        - **Chart**:
          - RDF: `<element type="chart" chartType="bar">`
          - JRXML: `<jr:barChart>`
        ...
        ```

        **Constraints**:
        - Ensure clarity for developers and report administrators.
        - Keep the document under 1000 words.
        - Include actionable troubleshooting steps.
        """
        doc_content = call_llm(prompt)
        with open(output_file, "w") as f:
            f.write(doc_content)
        print(f"Documentation saved to {output_file}")
    except Exception as e:
        print(f"Error generating documentation: {e}")

if __name__ == "__main__":
    generate_documentation("rdf_to_jrxml_mapping.json", "migration_doc.md")