import jinja2
import json
import requests
import os
import time
import re

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"  # Replace with your LLM API
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {"prompt": prompt, "max_tokens": 2000}
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

        **Task**: Generate a Jinja2 template for JasperReports JRXML that supports multiple queries, formulas, and element-specific datasets.

        **Input**:
        - Oracle RDF XML layout:
        ```xml
        {rdf_content[:1000]}
        ```
        - Mapping schema:
        ```json
        {json.dumps(mapping, indent=2)}
        ```
        - Context: Oracle RDF files contain multiple `<query>` elements with `queryName` or `id` attributes, linked to charts/tables via `queryRef`. Formulas are defined in `<formula>` elements.

        **Instructions**:
        1. Generate a Jinja2 template for JasperReports JRXML that includes:
           - `<subDataset>` elements for each query in `queries`, with `<queryString>` and `<field>` definitions.
           - `<variable>` elements for formulas in `formulas`, using JRXML expression syntax.
           - Chart elements (e.g., `<jr:barChart>`) and table elements (e.g., `<jr:table>`) linked to datasets via `datasetRun`.
           - Styling (borders, colors, fonts) using `<style>`, `<box>`, and `<font>` from `elements.properties`.
        2. Use ONLY the following Jinja2 variables: `queries`, `formulas`, `elements`, `namespace`.
        3. For chart datasets, use field names from `queries[].fields` (e.g., `$F{{{{queries[0].fields[0]}}}}`).
        4. Include namespaces (e.g., `http://jasperreports.sourceforge.net/jasperreports`).
        5. Ensure compatibility with JasperReports 6.x.
        6. Provide comments explaining the structure.
        7. Avoid undefined variables like `report_data`.

        **Expected Output**:
        A Jinja2 template string, e.g.:
        ```xml
        <?xml version="1.0" encoding="UTF-8"?>
        <jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:jr="http://jasperreports.sourceforge.net/jasperreports/components">
          <!-- Sub-datasets for multiple queries -->
          {% for q in queries %}
          <subDataset name="{{ q.id }}">
            <queryString language="SQL">
              <![CDATA[{{ q.sql }}]]>
            </queryString>
            {% for field in q.fields %}
            <field name="{{ field }}" class="java.lang.String"/>
            {% endfor %}
          </subDataset>
          {% endfor %}
          <!-- Formulas -->
          {% for formula in formulas %}
          <variable name="{{ formula.name }}" class="java.lang.Double">
            <variableExpression><![CDATA[{{ formula.expression }}]]></variableExpression>
          </variable>
          {% endfor %}
          <!-- Layout -->
          <detail>
            {% for elem in elements %}
            <band height="50">
              <{{ elem.type }} datasetRun="{{ elem.query_id }}">
                <reportElement x="0" y="0" width="200" height="50">
                  {% for prop, value in elem.properties.items() %}
                  <property name="{{ prop }}" value="{{ value }}"/>
                  {% endfor %}
                </reportElement>
                {% if elem.type == 'jr:barChart' %}
                <barChartDataset>
                  <dataset/>
                  <keyExpression><![CDATA[$F{{ '{{' }}{% for q in queries %}{% if q.id == elem.query_id %}{{ q.fields[0] }}{% endif %}{% endfor %}}]]></keyExpression>
                  <valueExpression><![CDATA[$F{{ '{{' }}{% for q in queries %}{% if q.id == elem.query_id %}{{ q.fields[1] }}{% endif %}{% endfor %}}]]></valueExpression>
                </barChartDataset>
                <barPlot/>
                {% endif %}
                {% if elem.type == 'jr:table' %}
                <jr:table>
                  <datasetRun subDataset="{{ elem.query_id }}"/>
                  {% for field in queries | selectattr('id', 'equalto', elem.query_id') | first | attr('fields') %}
                  <jr:column width="100">
                    <jr:columnHeader height="30">
                      <staticText>
                        <text><![CDATA[{{ field }}]]></text>
                      </staticText>
                    </jr:columnHeader>
                    <jr:detailCell height="30">
                      <textField>
                        <textFieldExpression><![CDATA[$F{{ '{{' }}{{ field }}}}]]></textFieldExpression>
                      </textField>
                    </jr:detailCell>
                  </jr:column>
                  {% endfor %}
                </jr:table>
                {% endif %}
              </{{ elem.type }}>
            </band>
            {% endfor %}
          </detail>
        </jasperReport>
        ```

        **Constraints**:
        - Ensure valid JRXML syntax.
        - Use only `queries`, `formulas`, `elements`, `namespace` as Jinja2 variables.
        - Support multiple queries with element-specific datasets.
        - Handle formulas as JRXML variables.
        - Keep the template concise and reusable.
        """
        template_content = call_llm(prompt)
        
        # Validate template for unexpected variables
        undefined_vars = re.findall(r'\{\{\s*(\w+)\s*\}\}', template_content)
        allowed_vars = {'queries', 'formulas', 'elements', 'namespace', 'prop', 'value', 'elem', 'q', 'field', 'formula'}
        invalid_vars = [var for var in undefined_vars if var not in allowed_vars]
        if invalid_vars:
            print(f"Warning: Template contains undefined variables: {invalid_vars}")
        
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

        **Task**: Extract metadata from an Oracle RDF XML file for migration to JasperReports, including multiple queries and formulas.

        **Input**:
        - Oracle RDF XML:
        ```xml
        {rdf_content[:1000]}
        ```
        - Mapping schema:
        ```json
        {json.dumps(mapping, indent=2)}
        ```
        - Context: Oracle RDF files contain multiple `<query>` elements with `queryName` or `id` attributes, linked to charts/tables via `queryRef`. Formulas are in `<formula>` elements.

        **Instructions**:
        1. Parse the RDF XML to extract:
           - All `<query>` elements, including `queryName` or index-based ID, SQL, and field names (e.g., `name`, `age`).
           - Chart elements from `<element type="chart" chartType="..." queryRef="...">` (e.g., type, chartType, style, color, font).
           - Table elements from `<element type="table" queryRef="...">` (e.g., style, font).
           - Formulas from `<formula>` elements (e.g., name, expression like `SUM(salary)`).
           - Styling attributes (style, color, font) for each element.
        2. Map RDF attributes to JRXML equivalents using the mapping schema.
        3. Return a JSON object with:
           - `queries`: List of query objects with `id`, `sql`, `fields` (e.g., `[{"id": "q1", "sql": "SELECT name, age ...", "fields": ["name", "age"]}]`).
           - `formulas`: List of formula objects with `name`, `expression` (e.g., `[{"name": "total_salary", "expression": "SUM(salary)"}]`).
           - `elements`: List of elements with `type`, `namespace`, `properties`, `query_id` (linked to a query `id`).
        4. Handle missing `queryRef` by mapping queries to elements by order (first query to first element, etc.).
        5. Include robust error handling for missing elements or malformed XML.
        6. Ensure compatibility with JasperReports 6.x.

        **Expected Output**:
        A JSON object, e.g.:
        ```json
        {{
          "queries": [
            {{"id": "q1", "sql": "SELECT name, age FROM employees WHERE dept = ?", "fields": ["name", "age"]}},
 evidence            {{"id": "q2", "sql": "SELECT dept, COUNT(*) AS emp_count FROM employees GROUP BY dept", "fields": ["dept", "emp_count"]}}
          ],
          "formulas": [
            {{"name": "total_age", "expression": "SUM(age)"}},
            {{"name": "age_plus_ten", "expression": "age + 10"}}
          ],
          "elements": [
            {{
              "type": "jr:barChart",
              "namespace": "http://jasperreports.sourceforge.net/jasperreports",
              "query_id": "q1",
              "properties": {{"border": "1.0", "color": "#FF0000", "fontName": "Arial", "size": "12", "isBold": "true"}}
            }},
            {{
              "type": "jr:table",
              "namespace": "http://jasperreports.sourceforge.net/jasperreports/components",
              "query_id": "q2",
              "properties": {{"fontName": "Arial", "size": "12"}}
            }}
          ]
        }}
        ```

        **Constraints**:
        - Do not use external libraries for parsing; rely on string analysis.
        - Handle edge cases (e.g., empty files, missing attributes, no queryRef).
        - Ensure compatibility with the mapping schema.
        """
        metadata = call_llm(prompt)
        return metadata
    except Exception as e:
        print(f"Error extracting metadata from {rdf_file}: {e}")
        return {"queries": [], "formulas": [], "elements": []}

def convert_rdf_to_jrxml(rdf_file, output_path):
    try:
        mapping = load_mapping()
        metadata = extract_rdf_metadata(rdf_file, mapping)
        
        # Validate LLM output
        if not isinstance(metadata, dict) or "queries" not in metadata or "formulas" not in metadata or "elements" not in metadata:
            raise ValueError("Invalid LLM metadata output: missing 'queries', 'formulas', or 'elements'")

        queries = metadata.get("queries", [])
        formulas = metadata.get("formulas", [])
        elements = metadata.get("elements", [])
        
        # Validate elements and query mappings
        for elem in elements:
            if not isinstance(elem, dict) or "type" not in elem or "properties" not in elem or "query_id" not in elem:
                raise ValueError(f"Invalid element in LLM output: {elem}")
            if elem["query_id"] not in [q["id"] for q in queries]:
                print(f"Warning: Element {elem['type']} references invalid query_id {elem['query_id']}")

        # Generate JRXML template
        template_content = generate_jrxml_template(rdf_file, mapping)
        template = jinja2.Template(template_content)
        
        # Render JRXML with extracted metadata
        jrxml_content = template.render(
            queries=queries,
            formulas=formulas,
            elements=elements,
            namespace="http://jasperreports.sourceforge.net/jasperreports"
        )
        
        # Save JRXML file
        with open(output_path, "w") as f:
            f.write(jrxml_content)
        print(f"Converted {rdf_file} to {output_path}")
    except Exception as e:
        print(f"Error converting {rdf_file}: {e}")
        # Log template content for debugging
        try:
            with open("jasper_template.jrxml", "r") as f:
                print(f"Template content:\n{f.read()}")
        except:
            print("Could not read jasper_template.jrxml for debugging")

if __name__ == "__main__":
    convert_rdf_to_jrxml("report.rdf", "output.jrxml")