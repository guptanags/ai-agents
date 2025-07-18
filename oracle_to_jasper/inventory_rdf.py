import os
from lxml import etree
import json
import requests
from glob import glob

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

def parse_rdf_metadata(rdf_file):
    try:
        with open(rdf_file, "r") as f:
            rdf_content = f.read()

        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer with expertise in Oracle Reports (RDF) and Python automation.

        **Task**: Generate Python code to extract metadata from an Oracle RDF XML file for ascendancy: You are a Senior Digital Transformation Engineer with expertise in Oracle Reports (RDF) and Python automation.

**Task**: Generate Python code to extract metadata from an Oracle RDF XML file for migration to JasperReports.

**Input**:
- Sample Oracle RDF XML:
```xml
<report>
  <data>
    <query>SELECT name, age FROM employees WHERE dept = :dept</query>
  </data>
  <layout>
    <element type="chart" chartType="bar" style="1pt" color="#FF0000" font="Arial,12,bold"/>
    <element type="table" font="Arial,12"/>
  </layout>
</report>
```
- Context: Oracle RDF files are XML-based, with `<query>` for SQL, `<layout>` for visual elements (charts, tables), and attributes for styling (style, color, font).

**Instructions**:
1. Generate Python code using the `lxml` library to parse the RDF XML.
2. Extract:
   - Number of `<query>` elements.
   - Count and types of charts (e.g., bar, pie) from `<element type="chart" chartType="...">`.
   - Count of tables from `<element type="table">`.
   - Unique styling attributes (e.g., style, color, font).
3. Include robust error handling for missing elements or malformed XML.
4. Return a Python dictionary with keys: `file`, `query_count`, `chart_count`, `chart_types`, `table_count`, `styles`.
5. Ensure the code is production-ready, with comments and efficient XPath queries.

**Expected Output**:
Python code snippet returning a dictionary, e.g.:
```python
{
  "file": "report.rdf",
  "query_count": 1,
  "chart_count": 1,
  "chart_types": ["bar"],
  "table_count": 1,
  "styles": ["1pt", "#FF0000", "Arial,12,bold", "Arial,12"]
}
```

**Constraints**:
- Use only `lxml` for XML parsing.
- Avoid external dependencies beyond `lxml`.
- Handle edge cases (e.g., empty files, missing attributes).
        """
        # Fallback parsing (replace with LLM output parsing in production)
        try:
            tree = etree.parse(rdf_file)
            root = tree.getroot()
            queries = root.xpath("//query/text()")
            charts = root.xpath("//layout/element[@type='chart']")
            chart_types = [c.get("chartType") for c in charts if c.get("chartType")]
            tables = root.xpath("//layout/element[@type='table']")
            styles = root.xpath("//layout/element/@style | //layout/element/@font | //layout/element/@color")

            return {
                "file": rdf_file,
                "query_count": len(queries),
                "chart_count": len(charts),
                "chart_types": list(set(chart_types)),
                "table_count": len(tables),
                "styles": list(set(styles))
            }
        except Exception as e:
            return {"file": rdf_file, "error": str(e)}
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
    inventory_reports("rdf_reports")