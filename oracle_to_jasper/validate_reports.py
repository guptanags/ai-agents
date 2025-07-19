import os
from lxml import etree
import subprocess
import json
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {"prompt": prompt, "max_tokens": 1000}
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

def compare_pdf_outputs(rdf_pdf, jrxml_pdf):
    try:
        result = subprocess.run(
            ["compare", "-metric", "AE", rdf_pdf, jrxml_pdf, "diff.png"],
            capture_output=True, text=True
        )
        pixel_diff = int(result.stderr.splitlines()[-1])
        return pixel_diff < 1000
    except Exception as e:
        print(f"Error comparing PDFs: {e}")
        return False

def validate_report(rdf_file, jrxml_file, rdf_pdf, jrxml_pdf):
    try:
        tree = etree.parse(jrxml_file)
        print(f"JRXML {jrxml_file} is syntactically valid")

        if not compare_pdf_outputs(rdf_pdf, jrxml_pdf):
            with open(rdf_file, "r") as f1, open(jrxml_file, "r") as f2:
                rdf_content, jrxml_content = f1.read(), f2.read()
            prompt = f"""
            **Persona**: You are a Senior Digital Transformation Engineer with expertise in report validation and JasperReports.

            **Task**: Generate a Python script to validate JasperReports JRXML output against Oracle RDF output and suggest fixes for discrepancies.

            **Input**:
            - Oracle RDF file:
            ```xml
            {rdf_content[:1000]}
            ```
            - JRXML file:
            ```xml
            {jrxml_content[:1000]}
            ```
            - Context: Validation involves comparing PDF outputs (visual) and query results (data). Visual discrepancies may involve styling or layout issues.

            **Instructions**:
            1. Generate a Python script to:
               - Compare query results using a Oracle database connection.
               - Compare PDF outputs using ImageMagick’s `compare` command.
            2. Suggest fixes for common visual discrepancies (e.g., font mismatch, chart size).
            3. Include error handling for database and ImageMagick failures.
            4. Provide comments explaining the validation process.
            5. Return a JSON object with:
               - `script`: The Python script.
               - `fixes`: A list of actionable fix steps.

            **Expected Output**:
            ```json
            {{
              "script": "import oracle.connector\\n...",
              "fixes": [
                "Adjust chart width to 200px in JRXML",
                "Update font to Arial in <style> element"
              ]
            }}
            ```

            **Constraints**:
            - Use `oracle-connector-python` for database access.
            - Ensure compatibility with ImageMagick 7.x.
            - Handle missing data or files gracefully.
            """
            response = call_llm(prompt)
            script = response.get("script", "")
            fixes = response.get("fixes", [])
            print(f"LLM Validation Script: {script}")
            print(f"LLM Suggested Fixes: {fixes}")
            print(f"Visual validation failed for {rdf_file} -> {jrxml_file}")
        else:
            print(f"Visual validation passed for {rdf_file} -> {jrxml_file}")
    except Exception as e:
        print(f"Validation error for {jrxml_file}: {e}")

if __name__ == "__main__":
    validate_report("report.rdf", "output.jrxml", "report.pdf", "output.pdf")