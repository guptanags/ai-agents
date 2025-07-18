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

def generate_mapping_schema(rdf_sample_file):
    try:
        with open(rdf_sample_file, "r") as f:
            rdf_content = f.read()

        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer specializing in Oracle Reports (RDF) to JasperReports migration.

        **Task**: Create a JSON mapping schema to convert Oracle RDF elements to JasperReports JRXML elements.

        **Input**:
        - Sample Oracle RDF XML:
        ```xml
        {rdf_content[:1000]}
        ```
        - JasperReports JRXML reference:
          - Charts: `<jr:barChart>`, `<jr:pieChart>` (namespace: `http://jasperreports.sourceforge.net/jasperreports`)
          - Tables: `<jr:table>` (namespace: `http://jasperreports.sourceforge.net/jasperreports/components`)
          - Styles: `<style forecolor="#FF0000">`, `<box pen.lineWidth="1.0">`
          - Fonts: `<font fontName="Arial" size="12" isBold="true">`
        - Context: Oracle RDF uses XML with `<query>` for SQL and `<layout>` for visual elements. JasperReports uses JRXML with specific elements and namespaces.

        **Instructions**:
        1. Generate a JSON mapping schema mapping:
           - RDF `<query>` to JRXML `<queryString>`.
           - RDF chart elements (e.g., `chartType="bar"`) to JRXML chart elements (e.g., `<jr:barChart>`).
           - RDF table elements to JRXML `<jr:table>`.
           - RDF styling attributes (style, color, font) to JRXML `<style>`, `<box>`, or `<font>`.
        2. Include a `value_mapping` section for attributes (e.g., `"1pt": "1.0"` for borders).
        3. Structure the JSON with `oracle_rdf` and `jasper_reports` sections.
        4. Provide comments explaining key mappings.
        5. Ensure the schema covers all common RDF elements and attributes.

        **Expected Output**:
        A JSON object, e.g.:
        ```json
        {{
          "oracle_rdf": {{
            "query": {{"element": "query", "output": "queryString"}},
            "chart": {{"bar": {{"element": "GRAPH", "type": "bar"}}}},
            "table": {{"element": "MATRIX"}},
            "style": {{"attribute": "style", "value_example": "1pt"}},
            "color": {{"attribute": "color", "value_example": "#FF0000"}},
            "font": {{"attribute": "font", "value_example": "Arial,12,bold"}}
          }},
          "jasper_reports": {{
            "query": {{"element": "queryString", "language": "SQL"}},
            "chart": {{"bar": {{"element": "jr:barChart", "namespace": "http://jasperreports.sourceforge.net/jasperreports"}}}},
            "table": {{"element": "jr:table", "namespace": "http://jasperreports.sourceforge.net/jasperreports/components"}},
            "style": {{"element": "box", "property": "pen.lineWidth", "value_mapping": {{"1pt": "1.0"}}}},
            "color": {{"element": "style", "property": "forecolor"}},
            "font": {{"element": "font", "property": "fontName", "value_mapping": {{"Arial,12,bold": {{"fontName": "Arial", "size": "12", "isBold": "true"}}}}}}
          }}
        }}
        ```

        **Constraints**:
        - Ensure compatibility with JasperReports 6.x.
        - Handle missing or undocumented RDF attributes gracefully.
        - Keep the JSON concise yet comprehensive.
        """
        mapping = call_llm(prompt)
        with open("rdf_to_jrxml_mapping.json", "w") as f:
            json.dump(mapping, f, indent=4)
        print("Mapping schema saved to rdf_to_jrxml_mapping.json")
        return mapping
    except Exception as e:
        print(f"Error generating mapping for {rdf_sample_file}: {e}")
        return {}

if __name__ == "__main__":
    generate_mapping_schema("sample.rdf")