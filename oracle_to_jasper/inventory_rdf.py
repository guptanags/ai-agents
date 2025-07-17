import os
from lxml import etree
import json
import requests  # Example for LLM API call

def call_llm(prompt):
    # Replace with your LLM API (e.g., xAI Grok API, OpenAI, etc.)
    api_url = "https://api.x.ai/v1/completions"  # Example URL
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.post(api_url, json={"prompt": prompt, "max_tokens": 500})
    return response.json().get("choices")[0].get("text")

def parse_rdf_metadata(rdf_file):
    try:
        # Read sample RDF content for LLM
        with open(rdf_file, "r") as f:
            rdf_content = f.read()

        # LLM prompt to generate XPath queries
        prompt = f"""
        Given the Oracle RDF XML content below, generate Python code with lxml to extract:
        - Number of queries
        - Chart types and their count
        - Styling attributes (e.g., style, color, font)
        Include error handling.
        RDF content:
        {rdf_content[:1000]}  # Limit to avoid token overflow
        """
        llm_response = call_llm(prompt)

        # Execute LLM-generated code (for illustration; eval with caution in production)
        exec(llm_response)  # Alternatively, parse LLM response to extract XPaths

        # Default parsing (fallback or LLM-refined)
        tree = etree.parse(rdf_file)
        root = tree.getroot()
        queries = root.xpath("//query/text()")
        charts = root.xpath("//layout/element[@type='chart']")
        tables = root.xpath("//layout/element[@type='table']")
        styles = root.xpath("//layout/element/@style | //layout/element/@font | //layout/element/@color")

        return {
            "file": rdf_file,
            "query_count": len(queries),
            "chart_count": len(charts),
            "table_count": len(tables),
            "styles": list(set(styles))
        }
    except Exception as e:
        return {"file": rdf_file, "error": str(e)}

def inventory_reports(input_dir):
    metadata_list = []
    for rdf_file in glob(os.path.join(input_dir, "*.rdf")):
        metadata = parse_rdf_metadata(rdf_file)
        metadata_list.append(metadata)
    with open("report_inventory.json", "w") as f:
        json.dump(metadata_list, f, indent=4)
    print("Inventory saved to report_inventory.json")
    return metadata_list

if __name__ == "__main__":
    from glob import glob
    inventory_reports("rdf_reports")