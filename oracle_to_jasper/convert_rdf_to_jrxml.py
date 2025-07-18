import time
from lxml import etree
import jinja2
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
            return response.json().get("choices")[0].get("text")
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

def convert_rdf_to_jrxml(rdf_file, output_path):
    try:
        mapping = load_mapping()
        rdf_tree = etree.parse(rdf_file)
        queries = rdf_tree.xpath("//query/text()")
        query_string = queries[0] if queries else ""
        elements = []
        for elem in rdf_tree.xpath("//layout/element"):
            elem_type = elem.get("type")
            style = elem.get("style")
            color = elem.get("color")
            font = elem.get("font")
            jasper_elem = {"type": "unknown", "properties": {}}
            if elem_type == "chart" and elem.get("chartType") in mapping.get("oracle_rdf", {}).get("chart", {}):
                chart_type = elem.get("chartType")
                jasper_elem["type"] = mapping["jasper_reports"]["chart"][chart_type]["element"]
                jasper_elem["namespace"] = mapping["jasper_reports"]["chart"][chart_type]["namespace"]
            elif elem_type == "table":
                jasper_elem["type"] = mapping["jasper_reports"]["table"]["element"]
                jasper_elem["namespace"] = mapping["jasper_reports"]["table"]["namespace"]
            if style:
                jasper_elem["properties"]["border"] = mapping["jasper_reports"]["style"]["value_mapping"].get(style, "1.0")
            if color:
                jasper_elem["properties"]["color"] = mapping["jasper_reports"]["color"].get("value_mapping", {}).get(color, "#000000")
            if font:
                font_props = mapping["jasper_reports"]["font"]["value_mapping"].get(font, {})
                jasper_elem["properties"].update(font_props)
            elements.append(jasper_elem)
        template = jinja2.Template(generate_jrxml_template(rdf_file, mapping))
        jrxml_content = template.render(query=query_string, elements=elements, namespace="http://jasperreports.sourceforge.net/jasperreports")
        with open(output_path, "w") as f:
            f.write(jrxml_content)
        print(f"Converted {rdf_file} to {output_path}")
    except Exception as e:
        print(f"Error converting {rdf_file}: {e}")

if __name__ == "__main__":
    convert_rdf_to_jrxml("report.rdf", "output.jrxml")