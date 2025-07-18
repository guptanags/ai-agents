import jinja2
import json
import requests
import os
import time

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"  # Replace with your LLM API
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {"prompt": prompt, "max_tokens": 1500}
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

def load_mapping():
    try:
        with open("rdf_to_jrxml_mapping.json") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading mapping: {e}")
        return {}

def generate_jrxml_template(rdf_file, mapping):
    try:
        with open(rdf_file, "r") as f:
            rdf_content = f.read()
        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer specializing in Oracle Reports (RDF) to JasperReports migration.

        **Task**: Generate a Jinja2 template for JasperReports JRXML based on an Oracle RDF layout and mapping schema.

        **Input**:
        - Oracle RDF XML layout:
        ```xml
        {rdf_content[:1000]}
        ```
        - Mapping schema:
        ```json
        {json.dumps(mapping, indent=2)}
        ```
        - Context: Oracle RDF defines report layouts with charts, tables, and styling. JasperReports uses JRXML with specific elements and namespaces.

        **Instructions**:
        1. Generate a Jinja2 template for JasperReports JRXML that includes:
           - A `<queryString>` for SQL queries.
           - Chart elements (e.g., `<jr:barChart>`) with dataset and plot configurations.
           - Table elements (e.g., `<jr:table>`).
           - Styling (borders, colors, fonts) using `<style>`, `<box>`, and `<font>`.
        2. Use the mapping schema to ensure accurate conversion.
        3. Include namespaces for JRXML elements.
        4. Ensure compatibility with JasperReports 6.x and support for Jinja2 variables (e.g., `{{ query }}`, `{{ elements }}`).
        5. Provide comments explaining the structure.

        **Expected Output**:
        A Jinja2 template string, e.g.:
        ```xml
        <?xml version="1.0" encoding="UTF-8"?>
        <jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:jr="http://jasperreports.sourceforge.net/jasperreports/components">
          <!-- Query -->
          <queryString language="SQL">
            <![CDATA[{{ query }}]]>
          </queryString>
          <!-- Layout -->
          <detail>
            {% for elem in elements %}
            <band height="50">
              <{{ elem.type }}>
                <reportElement x="0" y="0" width="200" height="50">
                  {% for prop, value in elem.properties.items() %}
                  <property name="{{ prop }}" value="{{ value }}"/>
                  {% endfor %}
                </reportElement>
                {% if elem.type == 'jr:barChart' %}
                <barChartDataset>
                  <dataset/>
                  <keyExpression><![CDATA[$F{{ '{{' }}name}}]]></keyExpression>
                  <valueExpression><![CDATA[$F{{ '{{' }}value}}]]></valueExpression>
                </barChartDataset>
                <barPlot/>
                {% endif %}
              </{{ elem.type }}>
            </band>
            {% endfor %}
          </detail>
        </jasperReport>
        ```

        **Constraints**:
        - Ensure valid JRXML syntax.
        - Support dynamic styling based on RDF attributes.
        - Keep the template concise and reusable.
        """
        template_content = call_llm(prompt)
        with open("jasper_template.jrxml", "w") as f:
            f.write(template_content)
        return template_content
    except Exception as e:
        print(f"Error generating template for {rdf_file}: {e}")
        return ""

def extract_rdf_metadata(rdf_file, mapping):
    try:
        with open(rdf_file, "r") as f:
            rdf_content = f.read()

        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer with expertise in Oracle Reports (RDF) and Python automation.

        **Task**: Extract metadata from an Oracle RDF XML file for migration to JasperReports.

        **Input**:
        - Oracle RDF XML:
        ```xml
        {rdf_content[:1000]}
        ```
        - Mapping schema:
        ```json
        {json.dumps(mapping, indent=2)}
        ```
        - Context: Oracle RDF files are XML-based, with `<query>` for SQL, `<layout>` for visual elements (charts, tables), and attributes for styling (style, color, font).

        **Instructions**:
        1. Parse the RDF XML to extract:
           - SQL queries from `<query>` elements (return the first query if multiple exist).
           - Chart elements from `<element type="chart" chartType="...">` (e.g., type, chartType, style, color, font).
           - Table elements from `<element type="table">` (e.g., style, font).
           - Styling attributes (style, color, font) for each element.
        2. Map RDF attributes to JasperReports equivalents using the mapping schema.
        3. Return a JSON object with:
           - `query`: The first SQL query (string).
           - `elements`: A list of elements, each with:
             - `type`: JRXML element type (e.g., "jr:barChart", "jr:table").
             - `namespace`: JRXML namespace (if applicable).
             - `properties`: Dictionary of mapped properties (e.g., border, color, fontName, size, isBold).
        4. Include robust error handling for missing elements or malformed XML.
        5. Ensure the output is compatible with JasperReports 6.x and the provided mapping schema.

        **Expected Output**:
        A JSON object, e.g.:
        ```json
        {{
          "query": "SELECT name, age FROM employees WHERE dept = ?",
          "elements": [
            {{
              "type": "jr:barChart",
              "namespace": "http://jasperreports.sourceforge.net/jasperreports",
              "properties": {{
                "border": "1.0",
                "color": "#FF0000",
                "fontName": "Arial",
                "size": "12",
                "isBold": "true"
              }}
            }},
            {{
              "type": "jr:table",
              "namespace": "http://jasperreports.sourceforge.net/jasperreports/components",
              "properties": {{
                "fontName": "Arial",
                "size": "12"
              }}
            }}
          ]
        }}
        ```

        **Constraints**:
        - Do not use external libraries for parsing; rely on string analysis.
        - Handle edge cases (e.g., empty files, missing attributes).
        - Ensure compatibility with the mapping schema.
        """
        metadata = call_llm(prompt)
        return metadata
    except Exception as e:
        print(f"Error extracting metadata from {rdf_file}: {e}")
        return {"query": "", "elements": []}

def convert_rdf_to_jrxml(rdf_file, output_path):
    try:
        mapping = load_mapping()
        metadata = extract_rdf_metadata(rdf_file, mapping)
        
        # Validate LLM output
        if not isinstance(metadata, dict) or "query" not in metadata or "elements" not in metadata:
            raise ValueError("Invalid LLM metadata output: missing 'query' or 'elements'")

        query_string = metadata.get("query", "")
        elements = metadata.get("elements", [])
        
        # Validate elements
        for elem in elements:
            if not isinstance(elem, dict) or "type" not in elem or "properties" not in elem:
                raise ValueError(f"Invalid element in LLM output: {elem}")

        # Generate JRXML template
        template_content = generate_jrxml_template(rdf_file, mapping)
        template = jinja2.Template(template_content)
        
        # Render JRXML with extracted metadata
        jrxml_content = template.render(
            query=query_string,
            elements=elements,
            namespace="http://jasperreports.sourceforge.net/jasperreports"
        )
        
        # Save JRXML file
        with open(output_path, "w") as f:
            f.write(jrxml_content)
        print(f"Converted {rdf_file} to {output_path}")
    except Exception as e:
        print(f"Error converting {rdf_file}: {e}")

if __name__ == "__main__":
    convert_rdf_to_jrxml("report.rdf", "output.jrxml")