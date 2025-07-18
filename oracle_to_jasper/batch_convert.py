import json
import os
from glob import glob
from multiprocessing import Pool
import requests
from convert_rdf_to_jrxml import convert_rdf_to_jrxml

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

def batch_convert_rdf_to_jrxml(input_dir, output_dir, template_path):
    try:
        os.makedirs(output_dir, exist_ok=True)
        tasks = []
        for rdf_file in glob(os.path.join(input_dir, "*.rdf")):
            output_file = os.path.join(output_dir, os.path.basename(rdf_file).replace(".rdf", ".jrxml"))
            tasks.append((rdf_file, template_path, output_file))

        prompt = f"""
        **Persona**: You are a Senior Digital Transformation Engineer with expertise in Python automation and report migration.

        **Task**: Optimize a Python script for batch processing Oracle RDF files to JasperReports JRXML using multiprocessing.

        **Input**:
        - Python script:
        ```python
        {open(__file__).read()}
        ```
        - Context: The script processes multiple RDF files in parallel to generate JRXML files.

        **Instructions**:
        1. Optimize the script for performance (e.g., adjust pool size, add logging).
        2. Add robust error handling for failed conversions (e.g., malformed XML, missing files).
        3. Include retry logic for transient failures.
        4. Provide comments explaining optimizations and error handling.
        5. Return the optimized Python script as a string.

        **Expected Output**:
        A Python script snippet, e.g.:
        ```python
        import os
        from glob import glob
        from multiprocessing import Pool
        import logging
        # Optimized script with logging and retries
        ...
        ```

        **Constraints**:
        - Use Python's `multiprocessing` and `logging` modules.
        - Ensure compatibility with Python 3.8+.
        - Keep the script scalable for large report volumes.
        """
        optimized_code = call_llm(prompt)
        print(f"LLM Optimization Suggestions: {optimized_code}")
        with Pool() as pool:
            pool.starmap(convert_rdf_to_jrxml, tasks)
        print(f"Batch conversion completed. Output in {output_dir}")
    except Exception as e:
        print(f"Error in batch conversion: {e}")

if __name__ == "__main__":
    batch_convert_rdf_to_jrxml("rdf_reports", "jrxml_reports", "jasper_template.jrxml")