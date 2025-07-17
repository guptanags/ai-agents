import jinja2
import json
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.post(api_url, json={"prompt": prompt, "max_tokens": 2000})
    return response.json().get("choices")[0].get("text")

def generate_documentation(mapping_file, output_file):
    with open(mapping_file) as f:
        mapping = json.load(f)

    # LLM prompt for documentation
    prompt = f"""
    Generate a Markdown documentation file for migrating Oracle RDF reports to JasperReports, including:
    - Overview of the process
    - Mapping schema details: {json.dumps(mapping, indent=2)}
    - Instructions for running scripts (inventory_rdf.py, convert_rdf_to_jrxml.py, etc.)
    - Troubleshooting tips
    """
    doc_content = call_llm(prompt)

    # Save documentation
    with open(output_file, "w") as f:
        f.write(doc_content)
    print(f"Documentation saved to {output_file}")

if __name__ == "__main__":
    generate_documentation("rdf_to_jrxml_mapping.json", "migration_doc.md")