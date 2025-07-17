import os
from lxml import etree
import subprocess
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.post(api_url, json={"prompt": prompt, "max_tokens": 500})
    return response.json().get("choices")[0].get("text")

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
            prompt = f"""
            The JasperReports PDF ({jrxml_pdf}) differs visually from the Oracle RDF PDF ({rdf_pdf}).
            Analyze potential causes (e.g., styling, layout) and suggest fixes for the JRXML file:
            {open(jrxml_file).read()[:1000]}
            """
            fixes = call_llm(prompt)
            print(f"LLM Suggested Fixes: {fixes}")
            print(f"Visual validation failed for {rdf_file} -> {jrxml_file}")
        else:
            print(f"Visual validation passed for {rdf_file} -> {jrxml_file}")

    except Exception as e:
        print(f"Validation error for {jrxml_file}: {e}")

if __name__ == "__main__":
    validate_report("report.rdf", "output.jrxml", "report.pdf", "output.pdf")