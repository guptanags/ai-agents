from core import prompt_expert
from core.action_context import ActionContext
from core.prompt import Prompt
from core.tool_decorator import register_tool


@register_tool(tags=["documentation"])
def generate_technical_documentation(action_context: ActionContext, code_or_feature: str) -> str:
    """
    Generate technical documentation by consulting a senior technical writer.
    This expert focuses on creating clear, comprehensive documentation for developers.
    
    Args:
        code_or_feature: The code or feature to document
    """
    return prompt_expert(
        action_context=action_context,
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
def design_test_suite(action_context: ActionContext, feature_description: str) -> str:
    """
    Design a comprehensive test suite by consulting a senior QA engineer.
    This expert focuses on creating thorough test coverage with attention to edge cases.
    
    Args:
        feature_description: Description of the feature to test
    """
    return prompt_expert(
        action_context=action_context,
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
def perform_code_review(action_context: ActionContext, code: str) -> str:
    """
    Review code and suggest improvements by consulting a senior software architect.
    This expert focuses on code quality, architecture, and best practices.
    
    Args:
        code: The code to review
    """
    return prompt_expert(
        action_context=action_context,
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
def write_feature_announcement(action_context: ActionContext, 
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
        action_context=action_context,
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

@register_tool()
def create_and_consult_expert(action_context: ActionContext, 
                             expertise_domain: str,
                             problem_description: str) -> str:
    """
    Dynamically create and consult an expert persona based on the specific domain and problem.
    
    Args:
        expertise_domain: The specific domain of expertise needed
        problem_description: Detailed description of the problem to be solved
        
    Returns:
        The expert's insights and recommendations
    """
    # Step 1: Dynamically generate a persona description
    persona_description_prompt = f"""
    Create a detailed description of an expert in {expertise_domain} who would be 
    ideally suited to address the following problem:
    
    {problem_description}
    
    Your description should include:
    - The expert's background and experience
    - Their specific areas of specialization within {expertise_domain}
    - Their approach to problem-solving
    - The unique perspective they bring to this type of challenge
    """
    
    generate_response = action_context.get("llm")
    persona_description = generate_response(Prompt(messages=[
        {"role": "user", "content": persona_description_prompt}
    ]))
    
    # Step 2: Generate a specialized consultation prompt
    consultation_prompt_generator = f"""
    Create a detailed consultation prompt for an expert in {expertise_domain} 
    addressing the following problem:
    
    {problem_description}
    
    The prompt should guide the expert to provide comprehensive insights and
    actionable recommendations specific to this problem.
    """
    
    consultation_prompt = generate_response(Prompt(messages=[
        {"role": "user", "content": consultation_prompt_generator}
    ]))
    
    # Step 3: Consult the dynamically created persona
    return prompt_expert(
        action_context=action_context,
        description_of_expert=persona_description,
        prompt=consultation_prompt
    )