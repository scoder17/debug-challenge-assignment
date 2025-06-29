## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from crewai.llm import LLM
from tools import search_tool, BloodTestReportTool

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature = 0.7
)

# Creating an Experienced Doctor agent
doctor = Agent(
    role="Senior Medical Professional and Blood Test Analyst",
    goal="Analyze blood test reports accurately and provide professional medical insights for query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced medical professional with 20+ years of experience in clinical medicine "
        "and laboratory diagnostics. You specialize in interpreting blood test results and providing "
        "evidence-based medical insights. You are thorough, accurate, and always prioritize patient safety. "
        "You provide clear explanations of blood test findings and their clinical significance, "
        "while emphasizing the importance of consulting with healthcare providers for proper medical advice."
    ),
    tools=[BloodTestReportTool()],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

# Creating a verifier agent
verifier = Agent(
    role="Medical Document Verifier",
    goal="Verify that uploaded documents are legitimate blood test reports and contain valid medical data",
    verbose=True,
    memory=True,
    backstory=(
        "You are a medical records specialist with expertise in document verification. "
        "You carefully review documents to ensure they are legitimate medical reports "
        "and contain properly formatted blood test data. You check for standard medical "
        "formatting, proper units, and realistic value ranges."
    ),
    tools=[BloodTestReportTool()],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)

nutritionist = Agent(
    role="Clinical Nutritionist",
    goal="Provide evidence-based nutritional recommendations based on blood test results",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified clinical nutritionist with expertise in interpreting blood biomarkers "
        "for nutritional assessment. You provide evidence-based dietary recommendations "
        "based on blood test results, focusing on nutrient deficiencies, metabolic markers, "
        "and overall health optimization through proper nutrition."
    ),
    tools=[BloodTestReportTool()],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)

exercise_specialist = Agent(
    role="Exercise Physiologist",
    goal="Provide safe, personalized exercise recommendations based on health markers from blood tests",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified exercise physiologist with expertise in designing safe, "
        "personalized exercise programs based on individual health markers. You consider "
        "blood test results to recommend appropriate exercise intensities and types "
        "while prioritizing safety and gradual progression."
    ),
    tools=[BloodTestReportTool()],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)