import os
import requests

def call_llm(prompt):
    api_url = "https://api.x.ai/v1/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    response = requests.post(api_url, json={"prompt": prompt, "max_tokens": 1000})
    return response.json().get("choices")[0].get("text")

def deploy_jrxml_to_server(jrxml_file, server_url, username, password):
    try:
        with open(jrxml_file, "r") as f:
            jrxml_content = f.read()

        # LLM prompt for deployment logic
        prompt = f"""
        Generate a Python script to deploy the following JRXML file to JasperReports Server using the REST API:
        {jrxml_content[:1000]}
        Include JDBC data source configuration for MySQL.
        """
        llm_response = call_llm(prompt)
        print(f"LLM Deployment Script: {llm_response}")

        # Default deployment
        headers = {"Content-Type": "text/xml"}
        response = requests.put(
            f"{server_url}/rest_v2/resources/reports/{os.path.basename(jrxml_file)}",
            auth=(username, password),
            data=jrxml_content,
            headers=headers
        )
        if response.status_code == 200:
            print(f"Deployed {jrxml_file} to {server_url}")
        else:
            print(f"Failed to deploy {jrxml_file}: {response.text}")
    except Exception as e:
        print(f"Error deploying {jrxml_file}: {e}")

if __name__ == "__main__":
    server_url = "http://localhost:8080/jasperserver"
    deploy_jrxml_to_server("output.jrxml", server_url, "jasperadmin", "jasperadmin")