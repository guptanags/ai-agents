import os
import re
from core.code_extractor import parse_markdown_and_create_structure
from core.prompt_expert import prompt_expert
from core.action_context import ActionContext
from core.prompt import Prompt
from core.tool_decorator import register_tool

# @register_tool(tags=["requirements"])
def generate_detailed_requirements( code_or_feature: str) -> str:
    """
    Generate detailed requirements specifications by consulting a senior product manager.
    This expert focuses on translating feature requests into actionable requirements.
    
    Args:
        code_or_feature: The code or feature to document
    """
    return prompt_expert(
        
        description_of_expert="""
        You are a senior product manager with extensive experience in translating feature requests into actionable requirements specifications.

        """,
        prompt=f"""
        Your task is to develop a detailed requirements specification for the following feature request:

{code_or_feature}

Please ensure your requirements specification includes:
1. **Feature Overview:** A clear summary of the feature and its purpose.
2. **User Stories:** Specific user stories or use cases that describe how different users will interact with the feature.
3. **Functional Requirements:** A comprehensive list of all functional requirements, including inputs, outputs, and system behaviors.
4. **Non-Functional Requirements:** Any relevant performance, security, usability, scalability, or reliability requirements.
5. **Acceptance Criteria:** Clear and measurable criteria that must be met for the feature to be considered complete.
6. **Dependencies & Constraints:** Any dependencies on other systems, teams, or technologies, and any constraints or limitations.
7. **Assumptions:** Any assumptions made during requirements gathering.
8. **Out-of-Scope:** Explicitly state what is not included in this feature.

Use clear, concise language suitable for both technical and non-technical stakeholders. Organize your response with headings and bullet points for readability.
        """
    )

# @register_tool(tags=["architecture"])
def generate_architecture_document( code_or_feature: str) -> str:
    """
    Generate architecture documentation by consulting a senior solution architect.
    This expert focuses on high-level architecture design, cloud strategy, and microservices.
    
    Args:
        code_or_feature: The code or feature to document
    """
    return prompt_expert(
      
        description_of_expert="""
        You are a senior solution architect with deep expertise in cloud-native architectures and microservices design.
        You have a strong background in translating business requirements into scalable, maintainable technical solutions.
        """,
        prompt=f"""
        Your task is to generate comprehensive architecture documentation for the following feature or system:

{code_or_feature}

Please ensure your documentation includes:
1. **Architecture Overview:** High-level summary of the system, its goals, and design principles.
2. **Cloud Strategy:** Explanation of cloud platform choice, deployment model (e.g., public, private, hybrid), and key cloud services used.
3. **Microservices Design:** Description of service boundaries, responsibilities, and interactions. Include diagrams or textual representations if possible.
4. **Data Flow & Integration:** How data moves between services, external integrations, and APIs.
5. **Scalability & Reliability:** Strategies for scaling, fault tolerance, and high availability.
6. **Security Considerations:** Authentication, authorization, data protection, and compliance.
7. **DevOps & CI/CD:** Approach to automation, deployment pipelines, and monitoring.       """
    )

# @register_tool(tags=["development"])
def implement_features(design_documentation: str) -> str:
    """
    Implement features based on design documentation by consulting a senior full stack developer.
    This expert focuses on both backend (Java/Spring Boot) and frontend (Angular) development.

    Args:
        code_or_feature: The code or feature to document
    """
    return prompt_expert(
        
        description_of_expert="""
        You are a full stack senior developer with deep expertise in Java (Spring Boot) for backend and Angular for frontend development.
        You have a strong background in translating architecture designs into scalable, maintainable code.""",
        prompt=f"""
        our task is to implement the following feature based on the provided architecture documentation:

{design_documentation}


Please ensure your implementation includes:
1. **Backend (Java/Spring Boot):**
   - Define RESTful APIs as described in the architecture.
   - Implement business logic, data models, and service layers.
   - Integrate with any required databases or external services.
   - Apply best practices for error handling, validation, and security.
2. **Frontend (Angular):**
   - Create Angular components, services, and modules as needed.
   - Implement UI/UX according to the architecture and feature requirements.
   - Ensure proper integration with backend APIs.
   - Handle state management and user interactions.
3. **Configuration & Integration:**
   - Provide configuration files for both backend and frontend.
   - Ensure smooth integration and communication between backend and frontend.
4. **Code Quality:**
   - Write clean, maintainable, and well-documented code.
   - Include comments and docstrings where appropriate.
   - Follow best practices for both Java and Angular development.
5. **Testing:**
   - Include unit and integration tests for critical components.


Instructions:
I need you to generate a project implementation with both backend (Spring Boot) and frontend (Angular) components for given Feature. The output should be structured as follows to allow easy extraction and file creation on my machine:
Do not incude project structure explicitely.

Example:

```java
filename: <<filename ( without directory path)>>
directory: <<directory where file needs to be created>>
package com.example.feedback;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class FeedbackSubmissionApplication 

```

```typescript
filename: <<filename ( without directory path)>>
directory: <<complete relative path project home to directory where file needs to be created>>
<<code>>
```
Guidelines:

Do not nest code blocks or mix narrative text with code content in the same block.
Use consistent indentation and file naming as shown in the PROJECT_STRUCTURE.
Avoid using square brackets [ ] or placeholders in code—write actual content or leave as empty implementations if necessary.
Include all necessary files as listed in the PROJECT_STRUCTURE, even if some are empty or placeholder implementations.
Do not include version control files (e.g., .gitignore) unless explicitly requested.
Output Format: Start with the PROJECT_STRUCTURE code block, followed by individual code blocks for each file in any order. Add a brief summary at the end explaining the implementation (outside code blocks).

Please generate the implementation for the Feedback Submission Feature based on this structure, including a Spring Boot backend with REST API, JPA for database interaction, and an Angular frontend with a feedback form. Assume a Oracle database and include basic configurations.
      """
    )


# @register_tool(tags=["documentation"])
def generate_technical_documentation(code_or_feature: str) -> str:
    """
    Generate technical documentation by consulting a senior technical writer.
    This expert focuses on creating clear, comprehensive documentation for developers.
    
    Args:
        code_or_feature: The code or feature to document
    """
    return prompt_expert(
        
        description_of_expert="""
        You are a senior technical writer with 15 years of experience in software documentation.
        You have particular expertise in:
        - Writing clear and precise API documentation
        - Explaining complex technical concepts to developers
        - Documenting implementation details and integration points
        - Creating code examples that illustrate key concepts
        - Identifying and documenting important caveats and edge cases
        
        Your documentation is known for striking the perfect balance between completeness
        and clarity. You understand that good technical documentation serves as both
        a reference and a learning tool.
        """,
        prompt=f"""
        Please create comprehensive technical documentation for the following code or feature:

        {code_or_feature}

        Your documentation should include:
        1. A clear overview of the feature's purpose and functionality
        2. Detailed explanation of the implementation approach
        3. Key interfaces and integration points
        4. Usage examples with code snippets
        5. Important considerations and edge cases
        6. Performance implications if relevant
        
        Focus on providing information that developers need to effectively understand
        and work with this code.
        """
    )

# @register_tool(tags=["testing"])
def design_test_suite(feature_description: str) -> str:
    """
    Design a comprehensive test suite by consulting a senior QA engineer.
    This expert focuses on creating thorough test coverage with attention to edge cases.
    
    Args:
        feature_description: Description of the feature to test
    """
    return prompt_expert(
      
        description_of_expert="""
        You are a senior QA engineer with 12 years of experience in test design and automation.
        Your expertise includes:
        - Comprehensive test strategy development
        - Unit, integration, and end-to-end testing
        - Performance and stress testing
        - Security testing considerations
        - Test automation best practices
        
        You are particularly skilled at identifying edge cases and potential failure modes
        that others might miss. Your test suites are known for their thoroughness and
        their ability to catch issues early in the development cycle.
        """,
        prompt=f"""
        Please design a comprehensive test suite for the following feature:

        {feature_description}

        Your test design should cover:
        1. Unit tests for individual components
        2. Integration tests for component interactions
        3. End-to-end tests for critical user paths
        4. Performance test scenarios if relevant
        5. Edge cases and error conditions
        6. Test data requirements
        
        For each test category, provide:
        - Specific test scenarios
        - Expected outcomes
        - Important edge cases to consider
        - Potential testing challenges
        """
    )

def generate_test_cases(test_strategy: str) -> str:
    """
    Generate test cases based on a description of the feature or code.
    
    Args:
        test_description: Description of the feature or code to test
    """
    return prompt_expert(
        description_of_expert="""
        You are a senior QA engineer with expertise in test case design and automation.
        You excel at creating comprehensive test cases that cover both functional and non-functional requirements.
        """,
        prompt=f"""
        I am a Senior QA Engineer with extensive experience in testing web applications, specializing in Java Spring Boot backend and Angular frontend development. My task is to create a comprehensive set of automated tests based on the provided test case specification included below. The application under test includes a Spring Boot backend with a REST API, JPA for database interaction, and an Angular frontend with interactive forms. I need you to generate the following test code based on the specification:

Unit Tests (Backend) with JUnit 5:
Use JUnit 5 as the testing framework.
Include Mockito for mocking dependencies (e.g., repositories, external services).
Cover all backend unit test scenarios listed, including expected outcomes, edge cases, and potential challenges.
Use an in-memory database (e.g., H2) for faster execution where applicable, and configure test-specific settings.
Address challenges such as time-sensitive tests with a fixed clock or filesystem interactions with mocks.
UI Tests (Frontend) with Jasmine:
Use Jasmine as the testing framework with Angular Testing Utilities.
Cover all frontend unit test scenarios listed, including expected outcomes, edge cases, and potential challenges.
Mock HTTP requests using jasmine-ajax or Angular's HttpClientTestingModule.
Handle asynchronous operations (e.g., Observables, Promises) and simulate user interactions (e.g., file input events).
Integration Tests (Backend) with Spring Test and Testcontainers:
Use Spring Test and Testcontainers to simulate a real database (e.g., Oracle or PostgreSQL).
Cover all backend integration test scenarios listed, including expected outcomes, edge cases, and potential challenges.
Use database transactions and rollback mechanisms to maintain a clean state.
Address challenges such as setting up the Spring context or managing test data.
Guidelines for Test Generation:

Structure: For each test, include a header comment with the test category, scenario, and purpose. Use meaningful test method names (e.g., shouldSaveFeedbackWithValidData).
Assertions: Include clear assertions using JUnit's Assertions or Jasmine's expect to verify expected outcomes.
Mocks and Stubs: Use Mockito for unit tests and Testcontainers for integration tests to isolate dependencies.
Edge Cases: Explicitly test the edge cases listed in the specification.
Configuration: Assume a typical application structure (e.g., backend package under com.example, frontend under src/app). Include necessary annotations (e.g., @SpringBootTest, @Test) and setup methods (e.g., @BeforeEach).
Output Format: Generate each test file as a separate code block with:
Example:

```java
filename: <<filename ( without directory path)>>
directory: <<complete relative path from project home to directory where file needs to be created>>
package com.example.feedback;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class FeedbackSubmissionApplication 

```

```typescript
filename: <<filename ( without directory path)>>
directory: <<directory where file needs to be created>>
<<code>>
```
The code content following these lines.
No Nesting: Avoid nesting code blocks or mixing narrative with code.
Test Data: Include sample test data (e.g., valid/invalid objects) as needed, inferred from the scenarios.
Assumptions:

The backend uses a package like com.example for services, controllers, and models.
The frontend is under src/app for components and services.
The database schema includes tables and columns relevant to the tested features (e.g., feedback table with feedbackId, subject, etc.).
External dependencies (e.g., file storage) can be mocked for unit tests.
Please generate the test code based on the following test case specification:

{test_strategy}

Adapt the tests to handle the challenges mentioned (e.g., asynchronous operations, file system mocks) and include comments explaining the approach for edge cases or complex scenarios. Ensure thorough coverage of all listed test scenarios."""
)


def develop_automation_tests(test_strategy: str) -> str:
    """
    Generate automations tests based on a description of the feature or code.
    
    Args:
        test_description: Description of the test strategy to implement
    """
    return prompt_expert(
        description_of_expert="""
        I am an Automation QA Expert with over a decade of experience in designing and implementing automated test frameworks for web and mobile applications. I specialize in JavaScript-based automation using WebdriverIO, with a strong focus on integrating testing tools like Sealights to optimize test execution and improve code coverage analysis. My task is to create a comprehensive automation test pack for a web application using WebdriverIO, integrated with Sealights for test optimization, based on the test case specification provided below. The application is a modern web app built with a JavaScript framework (e.g., React, Angular, or Vue.js), and the test pack will ensure robust end-to-end (E2E) testing, including edge cases and performance considerations.        """,
        prompt=f"""
        My task is to create a comprehensive automation test pack for a web application using WebdriverIO, integrated with Sealights for test optimization, based on the test case specification provided below. The application is a modern web app built with a JavaScript framework (e.g., React, Angular, or Vue.js), and the test pack will ensure robust end-to-end (E2E) testing, including edge cases and performance considerations.

I need you to generate the following automation test code based on the specification:

End-to-End Tests with WebdriverIO:
Use WebdriverIO as the test automation framework with Node.js, leveraging the WebDriver protocol and Chrome DevTools integration where applicable.
Implement tests using a test runner (e.g., Mocha, Jasmine, or Cucumber) and include smart selector strategies (e.g., CSS, XPath, or React/Angular/Vue-specific selectors).
Cover all E2E test scenarios listed in the specification, including expected outcomes, edge cases, and potential challenges.
Incorporate parallel test execution and automatic waiting mechanisms to enhance efficiency and reliability.
Address performance testing scenarios with basic metrics (e.g., response time, CPU usage) using DevTools or Lighthouse integration if specified.
Sealights Integration:
Integrate Sealights to assess and quantify code coverage for individual tests and optimize test execution by skipping irrelevant tests.
Configure the WebdriverIO test runner to send test execution details to Sealights using the Sealights Agent Token and appropriate CLI options (e.g., buildSessionId or labId).
Ensure the test pack supports Sealights' test optimization recommendations, automatically excluding tests as advised by Sealights during execution.
Include setup steps for Sealights Agents based on the application's framework (e.g., Node.js) and validate the integration in the test environment.
Guidelines for Test Generation:

Structure: For each test file, include a header comment with the test category (e.g., E2E), scenario, and purpose. Use descriptive test case names (e.g., shouldSubmitFeedbackSuccessfully).
Assertions: Use built-in WebdriverIO assertions or external libraries (e.g., Chai, Expect) to validate expected outcomes.
Selectors: Employ robust locator strategies (e.g., $(selector)) and consider accessibility selectors (e.g., aria-label) for better maintainability.
Edge Cases: Explicitly test edge cases listed in the specification (e.g., invalid inputs, network delays).
Configuration: Assume a typical WebdriverIO project structure (e.g., test/specs for test files) and include a wdio.conf.js configuration snippet if needed for Sealights integration.
Output Format: Generate each test file as a separate code block with:
The first line as the language (e.g., ```javascript
The second line as filename: <inferred_filename> (e.g., filename: feedbackE2ETest.js).
The third line as directory: <inferred_directory> (e.g., directory: test/specs/).
The test code content following these lines.
No Nesting: Avoid nesting code blocks or mixing narrative with code.
Test Data: Include sample test data (e.g., valid/invalid form inputs) inferred from the scenarios.
Assumptions:

The web application has a feedback form with fields like subject, description, email, and an optional file attachment.
The application is hosted locally or accessible via a test URL, with Chrome as the primary browser (extendable to others via configuration).
Sealights is configured with a valid Agent Token and URL, and the test environment supports Node.js-based automation.
External dependencies (e.g., API calls, file uploads) can be mocked or stubbed for controlled testing.
Sealights Integration Details:

Use the TestRail CLI or WebdriverIO CLI with Sealights options (e.g., --sealights-buildSessionId, --sealights-labId) to integrate test results.
Assume the test stage name is WebdriverIOAutomation unless overridden in the specification.
Ensure screenshots or logs are captured for failed tests to aid debugging, compatible with Sealights reporting.
Please generate the test code based on the following test case specification:

{test_strategy}
Adapt the tests to handle challenges mentioned (e.g., asynchronous operations, network issues) and include comments explaining the approach for edge cases, performance testing, or Sealights integration. Ensure the test pack is scalable, maintainable, and optimized for integration with Sealights."""
)

def develop_load_tests(test_strategy: str) -> str:
    """
    Generate load tests based on a description of the feature or code.
    
    Args:
        test_description: Description of the test strategy to implement
    """
    return prompt_expert(
        description_of_expert="""
       I am a Load Test Engineer with extensive experience in performance testing and optimization, specializing in Apache JMeter for designing and executing load tests on web applications. I have a deep understanding of performance metrics, scalability, and bottleneck identification, with a focus on ensuring applications can handle expected and peak user loads.""",
        prompt=f"""
        My task is to create a comprehensive load test suite for a web application using JMeter, based on the test strategy and performance testing scenarios provided below. The application is a modern web app (e.g., built with Spring Boot and Angular), and the test suite will simulate realistic user loads, measure performance metrics, and identify potential bottlenecks.

I need you to generate the following load test scripts based on the specification:

Load Tests with JMeter:
Use Apache JMeter as the load testing tool, configuring Thread Groups to simulate concurrent users.
Include HTTP Request samplers to target key endpoints (e.g., feedback submission API, feedback retrieval page) inferred from the test scenarios.
Implement timers (e.g., Gaussian Random Timer) to simulate realistic user think times.
Cover all performance testing scenarios listed in the specification, including expected metrics, thresholds, and potential challenges.
Use Listeners (e.g., View Results Tree, Aggregate Report) and Assertions (e.g., Response Assertion) to validate responses and collect performance data.
Address edge cases (e.g., high concurrency, network latency) and challenges (e.g., resource contention, database performance).
Test Configuration and Reporting:
Configure JMeter properties (e.g., jmeter.properties) for distributed testing if required, and include a basic test plan structure.
Generate CSV or JTL output files for performance metrics (e.g., response time, throughput, error rate) to analyze results.
Include comments explaining the approach for load patterns (e.g., ramp-up, steady state, peak load) and how thresholds are enforced.
Guidelines for Test Generation:

Structure: For each test script, include a header comment with the test category (e.g., Load Test), scenario, and purpose. Use descriptive test plan names (e.g., FeedbackLoadTestPlan).
Assertions: Include Response Assertions to verify HTTP status codes (e.g., 200 OK) and response content.
Parameters: Use CSV Data Set Config or User Parameters to inject dynamic test data (e.g., valid/invalid feedback inputs) inferred from the scenarios.
Edge Cases: Explicitly test edge cases listed in the specification (e.g., 100 concurrent users, sustained load over time).
Configuration: Assume a typical JMeter project structure (e.g., test/plans for test plans) and include necessary elements (e.g., HTTP Request Defaults, Thread Group).
Output Format: Generate each test script as a separate code block with:
The first line as the language (e.g., ```xml
The second line as filename: <inferred_filename> (e.g., filename: FeedbackLoadTestPlan.jmx).
The third line as directory: <inferred_directory> (e.g., directory: test/plans/).
The test script content (in JMeter .jmx XML format) following these lines.
No Nesting: Avoid nesting code blocks or mixing narrative with code.
Test Data: Include sample test data (e.g., feedback payloads) as needed, inferred from the scenarios.
Assumptions:

The web application has a REST API with endpoints like /api/feedback/submit and /api/feedback/all.
The application is hosted on a test URL (e.g., http://localhost:8080 or a staging environment), with Chrome as the browser context for HTTP requests.
Performance thresholds (e.g., response time < 2 seconds, error rate < 1%) are defined in the specification.
External dependencies (e.g., database, file storage) can introduce bottlenecks under load.
Additional Considerations:

Use HTTP Cookie Manager and HTTP Cache Manager to simulate realistic browser behavior.
Include a Summary Report listener to aggregate results and identify trends.
Ensure the test plan supports distributed testing with multiple JMeter instances if specified.
Please generate the load test scripts based on the following test strategy and performance testing specification:

{test_strategy}
Adapt the tests to handle challenges mentioned (e.g., resource contention, database performance) and include comments explaining the approach for load patterns, threshold enforcement, or distributed testing setup. Ensure the test suite is scalable, repeatable, and optimized for analyzing performance under various load conditions."""
)

# @register_tool(tags=["code_quality"])
def perform_code_review( code: str) -> str:
    """
    Review code and suggest improvements by consulting a senior software architect.
    This expert focuses on code quality, architecture, and best practices.
    
    Args:
        code: The code to review
    """
    return prompt_expert(
        
        description_of_expert="""
        You are a senior software architect with 20 years of experience in code review
        and software design. Your expertise includes:
        - Software architecture and design patterns
        - Code quality and maintainability
        - Performance optimization
        - Scalability considerations
        - Security best practices
        
        You have a talent for identifying subtle design issues and suggesting practical
        improvements that enhance code quality without over-engineering.
        """,
        prompt=f"""
        Please review the following code and provide detailed improvement suggestions:

        {code}

        Consider and address:
        1. Code organization and structure
        2. Potential design pattern applications
        3. Performance optimization opportunities
        4. Error handling completeness
        5. Edge case handling
        6. Maintainability concerns
        
        For each suggestion:
        - Explain the current issue
        - Provide the rationale for change
        - Suggest specific improvements
        - Note any trade-offs to consider
        """
    )

# @register_tool(tags=["communication"])
def write_feature_announcement(
                             feature_details: str,
                             audience: str) -> str:
    """
    Write a feature announcement by consulting a product marketing expert.
    This expert focuses on clear communication of technical features to different audiences.
    
    Args:
        feature_details: Technical details of the feature
        audience: Target audience for the announcement (e.g., "technical", "business")
    """
    return prompt_expert(
    
        description_of_expert="""
        You are a senior product marketing manager with 12 years of experience in
        technical product communication. Your expertise includes:
        - Translating technical features into clear value propositions
        - Crafting compelling product narratives
        - Adapting messaging for different audience types
        - Building excitement while maintaining accuracy
        - Creating clear calls to action
        
        You excel at finding the perfect balance between technical accuracy and
        accessibility, ensuring your communications are both precise and engaging.
        """,
        prompt=f"""
        Please write a feature announcement for the following feature:

        {feature_details}

        This announcement is intended for a {audience} audience.

        Your announcement should include:
        1. A compelling introduction
        2. Clear explanation of the feature
        3. Key benefits and use cases
        4. Technical details (adapted to audience)
        5. Implementation requirements
        6. Next steps or call to action
        
        Ensure the tone and technical depth are appropriate for a {audience} audience.
        Focus on conveying both the value and the practical implications of this feature.
        """
    )

def write_to_file(name: str, content: str) -> str:
    """Writes content to a specified file."""
    try:
        with open(name, "w") as f:
            f.write(content)
            print(f"File '{name}' written successfully.")  # Debug print
        return f"File '{name}' written successfully."
    except Exception as e:
        print(f"Error writing file '{name}': {e}")
        return f"Error writing file '{name}': {e}"

@register_tool(tags=["feature_development"])
def develop_feature( feature_request: str) -> dict:
    """
    Process a feature request through a chain of expert personas.
    """
    # Step 1: Product expert defines requirements
    requirements = generate_detailed_requirements(
       
        feature_request
    )
    
    # Write requirements to a file
    write_to_file("requirements.md", requirements)

    # Step 2: Architecture expert designs the solution
    architecture = generate_architecture_document(
  
        requirements
    )
    # Write architecture to a file
    write_to_file("architecture.md", architecture) 
    
    # Step 3: Developer expert implements the code
    implementation = implement_features(
     
        architecture
    )

    # Write implementation to a file
    write_to_file  ("implementation.md", implementation)
    parse_markdown_and_create_structure(implementation)
    # segregate_code_to_files( implementation)

    # Step 4: QA expert creates test cases
    tests = design_test_suite(
        
       
        f"Create test cases for this implementation: {implementation}"
    )
    # Write tests to a file 
    write_to_file("tests.md", tests)

    # Step 5: Test expert generates test cases
    test_cases = generate_test_cases(tests)
    # Write test cases to a file
    write_to_file("test_cases.md", test_cases)
    # Parse test cases and create structure
    parse_markdown_and_create_structure(test_cases)

    # Step 6: Automation expert develops automation tests
    # This step assumes the test strategy is provided in the tests variable
    automation_tests = develop_automation_tests(tests)
    # Write automation tests to a file
    write_to_file("automation_tests.md", automation_tests)
    parse_markdown_and_create_structure(automation_tests)
    
    # Step 7: Load test expert creates load tests
    load_tests = develop_load_tests(tests)
    # Write load tests to a file
    write_to_file("load_tests.md", load_tests)
    parse_markdown_and_create_structure(load_tests)

    # Step 8: Documentation expert creates documentation
    documentation = generate_technical_documentation(
        
        f"Document this implementation: {implementation}"
    )
    # Write documentation to a file
    write_to_file("documentation.md", documentation)    
    return {
        "requirements": requirements,
        "architecture": architecture,
        "implementation": implementation,
        "tests": tests,
        "documentation": documentation
    }

