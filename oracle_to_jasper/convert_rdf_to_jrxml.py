from lxml import etree
import jinja2
import json
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.post(api_url, json={"prompt": prompt, "max_tokens": 1000})
    return response.json().get("choices")[0].get("text")

def load_mapping():
    with open("rdf_to_jrxml_mapping.json") as f:
        return json.load(f)

def generate_jrxml_template(rdf_file, mapping):
    with open(rdf_file, "r") as f:
        rdf_content = f.read()
    prompt = f"""
    Given the Oracle RDF XML:
    {rdf_content[:1000]}
    And the mapping schema:
    {json.dumps(mapping, indent=2)}
    Generate a Jinja2 template for JasperReports JRXML with detailed chart configurations (e.g., barChart with dataset and plot) and styling (borders, colors, fonts).
    """
    template_content = call_llm(prompt)
    with open("jasper_template.jrxml", "w") as f:
        f.write(template_content)
    return template_content

def convert_rdf_to_jrxml(rdf_file, output_path):
    try:
        mapping = load_mapping()
        rdf_tree = etree.parse(rdf_file)
        
        # Generate template dynamically
        template_content = generate_jrxml_template(rdf_file, mapping)
        template = jinja2.Template(template_content)

        # Extract queries and elements
        queries = rdf_tree.xpath("//query/text()")
        query_string = queries[0] if queries else ""
        elements = []
        for elem in rdf_tree.xpath("//layout/element"):
            elem_type = elem.get("type")
            style = elem.get("style")
            color = elem.get("color")
            font = elem.get("font")
            jasper_elem = {"type": "unknown", "properties": {}}
            if elem_type == "GRAPH" and elem.get("chartType") in mapping["oracle_rdf"]["chart"]:
                chart_type = elem.get("chartType")
                jasper_elem["type"] = mapping["jasper_reports"]["chart"][chart_type]["element"]
                jasper_elem["namespace"] = mapping["jasper_reports"]["chart"][chart_type]["namespace"]
            elif elem_type == "MATRIX":
                jasper_elem["type"] = mapping["jasper_reports"]["table"]["element"]
                jasper_elem["namespace"] = mapping["jasper_reports"]["table"]["namespace"]
            if style:
                jasper_elem["properties"]["border"] = mapping["jasper_reports"]["border"]["value_mapping"].get(style, "1.0")
            if color:
                jasper_elem["properties"]["color"] = mapping["jasper_reports"]["color"]["value_mapping"].get(color, "#000000")
            if font:
                font_props = mapping["jasper_reports"]["font"]["value_mapping"].get(font, {})
                jasper_elem["properties"].update(font_props)
            elements.append(jasper_elem)

        # Render JRXML
        jrxml_content = template.render(query=query_string, elements=elements, namespace="http://jasperreports.sourceforge.net/jasperreports")
        with open(output_path, "w") as f:
            f.write(jrxml_content)
        print(f"Converted {rdf_file} to {output_path}")
    except Exception as e:
        # LLM debug prompt
        prompt = f"Debug the following Python error in RDF to JRXML conversion:\n{str(e)}\nCode context:\n{open(__file__).read()}"
        debug_suggestion = call_llm(prompt)
        print(f"LLM Debug Suggestion: {debug_suggestion}")
        print(f"Error converting {rdf_file}: {e}")

if __name__ == "__main__":
    convert_rdf_to_jrxml("report.rdf", "output.jrxml")