# Oracle RDF to JasperReports Migration

## Overview
This document outlines the automated process for migrating Oracle Reports (RDF) to JasperReports, enabling modern, scalable reporting with minimal manual effort. The process uses Python scripts to inventory, convert, validate, and deploy reports.

## Process Description
The migration involves the following steps:
1. **Inventory**: Catalog RDF reports and extract metadata (queries, charts, tables, styles).
2. **Mapping**: Define a JSON schema to map RDF elements to JRXML elements.
3. **Conversion**: Convert RDF files to JRXML using a Jinja2 template.
4. **SQL Validation**: Extract and validate SQL queries for MySQL compatibility.
5. **Validation**: Compare JRXML outputs against RDF outputs (data and visuals).
6. **Batch Processing**: Process multiple RDF files in parallel.
7. **Deployment**: Deploy JRXML files to JasperReports Server with JDBC configuration.

## Mapping Schema
The mapping schema (`rdf_to_jrxml_mapping.json`) defines conversions:
- **Query**:
  - RDF: `<query>SELECT name, age FROM employees</query>`
  - JRXML: `<queryString language="SQL">SELECT name, age FROM employees</queryString>`
- **Chart**:
  - RDF: `<element type="chart" chartType="bar" style="1pt" color="#FF0000" font="Arial,12,bold"/>`
  - JRXML: `<jr:barChart>` with `<box pen.lineWidth="1.0">`, `<style forecolor="#FF0000">`, `<font fontName="Arial" size="12" isBold="true">`
- **Table**:
  - RDF: `<element type="table" font="Arial,12"/>`
  - JRXML: `<jr:table>`

## Script Instructions
1. **Inventory**:
   ```bash
   python inventory_rdf.py rdf_reports
   ```
   - Output: `report_inventory.json`
2. **Mapping**:
   ```bash
   python generate_mapping.py sample.rdf
   ```
   - Output: `rdf_to_jrxml_mapping.json`
3. **Conversion**:
   ```bash
   python convert_rdf_to_jrxml.py report.rdf output.jrxml
   ```
   - Output: `output.jrxml`
4. **SQL Validation**:
   ```bash
   python extract_sql.py report.rdf queries.sql MySQL
   ```
   - Output: `queries.sql`, `jdbc_config_*.xml`
5. **Validation**:
   ```bash
   python validate_reports.py report.rdf output.jrxml report.pdf output.pdf
   ```
6. **Batch Processing**:
   ```bash
   python batch_convert.py rdf_reports jrxml_reports jasper_template.jrxml
   ```
   - Output: JRXML files in `jrxml_reports`
7. **Deployment**:
   ```bash
   python deploy_reports.py output.jrxml http://localhost:8080/jasperserver jasperadmin jasperadmin
   ```

## Troubleshooting Tips
- **XML Parsing Error**:
  - Check RDF file syntax and encoding.
  - Use `xmllint --format file.rdf` to validate.
- **SQL Compatibility**:
  - Replace Oracle bind variables (`:var`) with `?` for MySQL.
  - Test queries in MySQL Workbench.
- **Visual Discrepancies**:
  - Verify font mappings in `rdf_to_jrxml_mapping.json`.
  - Adjust JRXML element dimensions (e.g., `<reportElement width="200">`).
- **API Failures**:
  - Check JasperReports Server URL and credentials.
  - Increase retry attempts in `deploy_reports.py`.

For further assistance, contact the migration team or refer to JasperReports documentation.