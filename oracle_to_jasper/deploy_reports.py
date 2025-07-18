import os
import requests
import json

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

def deploy_jrxml_to_server(jrxml_file, server_url, username, password):
    try:
        with open(jrxml_file, "r") as f:
            jrxml_content = f.read()

        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer with expertise in JasperReports Server integration.

        **Task**: Generate a Python script to deploy a JRXML file to JasperReports Server and configure a MySQL JDBC data source.

        **Input**:
        - JRXML file snippet:
        ```xml
        {jrxml_content[:1000]}
        ```
        - Context: JasperReports Server uses a REST API (v2) for deploying reports and supports JDBC data sources.

        **Instructions**:
        1. Generate a Python script using `requests` to deploy the JRXML file via the REST API.
        2. Include a MySQL JDBC data source configuration XML.
        3. Provide authentication handling (e.g., username/password).
        4. Include error handling for API failures with retry logic.
        5. Provide comments explaining the deployment and configuration process.
        6. Return a JSON object with:
           - `script`: The Python script.
           - `jdbc_config`: The JDBC configuration XML.

        **Expected Output**:
        ```json
        {{
          "script": "import requests\\n...",
          "jdbc_config": "<dataSource name=\\"myDataSource\\" class=\\"com.mysql.jdbc.jdbc2.optional.MysqlDataSource\\" url=\\"jdbc:mysql://localhost:3306/db\\" user=\\"user\\" password=\\"pass\\"/>"
        }}
        ```

        **Constraints**:
        - Ensure compatibility with JasperReports Server 6.x.
        - Use the REST API v2 endpoint.
        - Handle transient API errors with retries.
        """
        response = call_llm(prompt)
        script = response.get("script", "")
        jdbc_config = response.get("jdbc_config", "")
        print(f"LLM Deployment Script: {script}")
        with open(f"jdbc_config_{os.path.basename(jrxml_file)}.xml", "w") as f:
            f.write(jdbc_config)

        headers = {"Content-Type": "text/xml"}
        for attempt in range(3):
            try:
                response = requests.put(
                    f"{server_url}/rest_v2/resources/reports/{os.path.basename(jrxml_file)}",
                    auth=(username, password),
                    data=jrxml_content,
                    headers=headers
                )
                response.raise_for_status()
                print(f"Deployed {jrxml_file} to {server_url}")
                break
            except requests.exceptions.RequestException as e:
                print(f"Deployment error (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    print(f"Failed to deploy {jrxml_file}: {e}")
    except Exception as e:
        print(f"Error deploying {jrxml_file}: {e}")

if __name__ == "__main__":
    server_url = "http://localhost:8080/jasperserver"
    deploy_jrxml_to_server("output.jrxml", server_url, "jasperadmin", "jasperadmin")