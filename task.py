## Importing libraries and files
from crewai import Task
from agents import doctor, verifier
from tools import BloodTestReportTool

## Creating a task to help solve user's query
help_patients = Task(
    description="""Analyze the blood test report and provide comprehensive medical insights for the user's query: {query}

    Your analysis should include:
    1. Read and interpret the blood test report from the file path: {file_path}
    2. Identify key blood markers and their values
    3. Explain what the results mean in medical terms
    4. Highlight any abnormal values and their potential significance
    5. Provide general health recommendations based on the findings
    6. Address the specific user query: {query}
    
    Always emphasize that this analysis is for informational purposes only and that users should consult with their healthcare providers for proper medical advice and treatment decisions.""",

    expected_output="""A comprehensive blood test analysis report that includes:

    ## Blood Test Analysis Summary
    - Overview of the report and key findings
    - List of blood markers tested and their values
    - Identification of normal vs. abnormal ranges
    
    ## Medical Interpretation
    - Clinical significance of the results
    - Explanation of any abnormal findings
    - Potential health implications
    
    ## Recommendations
    - General health and lifestyle recommendations
    - Suggestions for follow-up testing if needed
    - Dietary and lifestyle modifications that may be beneficial
    
    ## Important Disclaimer
    - Clear statement that this is for informational purposes only
    - Recommendation to consult with healthcare providers
    - Note that AI analysis should not replace professional medical advice

    The response should be professional, accurate, and helpful while maintaining appropriate medical disclaimers.""",

    agent=doctor,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

## Creating a nutrition analysis task
nutrition_analysis = Task(
    description="""Analyze the blood test report and provide evidence-based nutritional recommendations.

    Focus on:
    1. Nutrient deficiency markers (B vitamins, Vitamin D, Iron, etc.)
    2. Metabolic markers (glucose, lipids, etc.)
    3. Inflammatory markers that may be affected by diet
    4. Provide specific, actionable dietary recommendations
    5. Address the user's specific query: {query}
    
    Base all recommendations on established nutritional science and evidence-based practices.""",

    expected_output="""A detailed nutritional analysis including:
    
    ## Nutritional Assessment
    - Analysis of nutrient-related blood markers
    - Identification of potential deficiencies or excesses
    - Metabolic health indicators
    
    ## Dietary Recommendations
    - Specific foods to include or avoid
    - Meal planning suggestions
    - Timing recommendations for optimal health
    
    ## Supplement Considerations
    - Evidence-based supplement recommendations if appropriate
    - Dosage guidelines based on blood levels
    - Safety considerations and interactions
    
    All recommendations should be evidence-based and include appropriate disclaimers about consulting healthcare providers.""",

    agent=doctor,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

## Creating an exercise planning task
exercise_planning = Task(
    description="""Create a safe, personalized exercise plan based on blood test results and health markers.

    Consider:
    1. Cardiovascular health markers
    2. Metabolic indicators
    3. Inflammatory markers
    4. Energy and recovery markers
    5. Any contraindications for exercise
    6. User's specific query: {query}
    
    Prioritize safety and gradual progression while providing effective exercise recommendations.""",

    expected_output="""A comprehensive exercise plan including:
    
    ## Health Assessment for Exercise
    - Review of relevant blood markers for exercise planning
    - Identification of any exercise considerations or limitations
    - Baseline fitness assessment based on available data
    
    ## Exercise Recommendations
    - Cardiovascular exercise guidelines
    - Strength training recommendations
    - Flexibility and mobility work
    - Recovery and rest recommendations
    
    ## Safety Considerations
    - Precautions based on blood test results
    - Warning signs to watch for during exercise
    - When to modify or stop exercise
    
    ## Progressive Plan
    - Starting intensity and duration
    - Progression timeline
    - Monitoring recommendations
    
    Include appropriate medical disclaimers and recommendations to consult healthcare providers before starting new exercise programs.""",

    agent=doctor,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

## Creating a verification task
verification = Task(
    description="""Verify that the uploaded document is a legitimate blood test report and validate its contents.

    Check for:
    1. Proper medical report formatting
    2. Presence of standard blood test markers
    3. Realistic value ranges for reported tests
    4. Professional medical formatting and terminology
    5. Laboratory information and reference ranges
    
    Ensure the document contains actual medical data before proceeding with analysis.""",

    expected_output="""A verification report that includes:
    
    ## Document Verification
    - Confirmation that the document is a blood test report
    - Assessment of document authenticity and formatting
    - Identification of key blood markers present
    
    ## Data Quality Assessment
    - Validation of blood marker values and ranges
    - Check for completeness of report
    - Assessment of data reliability
    
    ## Verification Status
    - Clear statement of whether the document is verified as a blood test report
    - Any concerns or limitations identified
    - Recommendations for proceeding with analysis
    
    If the document is not a valid blood test report, clearly state this and explain why analysis cannot proceed.""",

    agent=verifier,
    tools=[BloodTestReportTool()],
    async_execution=False
)