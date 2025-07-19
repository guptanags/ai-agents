from core.prompt_expert import prompt_expert
from core.action_context import ActionContext
from core.prompt import Prompt
from core.tool_decorator import register_tool

@register_tool(tags=["requirements"])
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

@register_tool(tags=["architecture"])
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

@register_tool(tags=["development"])
def implement_features(architecture_documentation: str) -> str:
    """
    Implement features based on architecture documentation by consulting a senior full stack developer.
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

{architecture_documentation}

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
      """
    )


@register_tool(tags=["documentation"])
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

@register_tool(tags=["testing"])
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

@register_tool(tags=["code_quality"])
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

@register_tool(tags=["communication"])
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



@register_tool(tags=["feature_development"])
def develop_feature( feature_request: str) -> dict:
    """
    Process a feature request through a chain of expert personas.
    """
    # Step 1: Product expert defines requirements
    requirements = generate_detailed_requirements(
       
        feature_request
    )
    
    # Step 2: Architecture expert designs the solution
    architecture = generate_architecture_document(
  
        requirements
    )
    
    # Step 3: Developer expert implements the code
    implementation = develop_feature(
     
        architecture
    )
    
    # Step 4: QA expert creates test cases
    tests = design_test_suite(
        
       
        f"Create test cases for this implementation: {implementation}"
    )
    
    # Step 5: Documentation expert creates documentation
    documentation = generate_technical_documentation(
        
        f"Document this implementation: {implementation}"
    )
    
    return {
        "requirements": requirements,
        "architecture": architecture,
        "implementation": implementation,
        "tests": tests,
        "documentation": documentation
    }