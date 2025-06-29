## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class BloodTestReportToolInput(BaseModel):
    """Input schema for BloodTestReportTool."""
    path: str = Field(default='data/sample.pdf', description="Path of the PDF file containing the blood test report")

class BloodTestReportTool(BaseTool):
    name: str = "Read Blood Test Report"
    description: str = "Tool to read data from a PDF file containing blood test results"
    args_schema: Type[BaseModel] = BloodTestReportToolInput
    
    def _run(self, path: str = 'data/sample.pdf') -> str:
        """Tool to read data from a PDF file containing blood test results.

        Args:
            path (str): Path of the PDF file containing the blood test report.

        Returns:
            str: Extracted text content from the blood test report PDF file.
        """
        try:
            if not os.path.exists(path):
                return f"Error: File not found at path: {path}"
            
            # Load PDF using PyPDFLoader
            loader = PyPDFLoader(file_path=path)
            docs = loader.load()

            if not docs:
                return f"Error: No content could be extracted from the PDF file at {path}"

            full_report = ""
            for doc in docs:
                # Clean and format the report data
                content = doc.page_content
                
                # Remove extra whitespaces and format properly
                content = content.replace('\n\n', '\n').strip()
                full_report += content + "\n"
                
            return full_report.strip() if full_report.strip() else "Error: PDF file appears to be empty or unreadable"
            
        except Exception as e:
            return f"Error reading PDF file: {str(e)}"

## Creating Nutrition Analysis Tool
class NutritionToolInput(BaseModel):
    """Input schema for NutritionTool."""
    blood_report_data: str = Field(description="Blood test report data for nutrition analysis")

class NutritionTool(BaseTool):
    name: str = "Analyze Nutrition from Blood Report"
    description: str = "Analyze blood report data and provide nutritional insights"
    args_schema: Type[BaseModel] = NutritionToolInput
    
    def _run(self, blood_report_data: str) -> str:
        """Analyze blood report data and provide nutritional insights.
        
        Args:
            blood_report_data (str): Blood test report data
            
        Returns:
            str: Nutrition analysis based on blood markers
        """
        try:
            # Process and analyze the blood report data
            processed_data = blood_report_data.strip()
            
            if not processed_data:
                return "Error: No blood report data provided for nutrition analysis"
            
            # TODO: Implement comprehensive nutrition analysis logic here
            # This would include analyzing various blood markers like:
            # - Vitamin levels (B12, D, etc.)
            # - Mineral levels (Iron, Magnesium, etc.)
            # - Lipid profiles
            # - Blood sugar levels
            
            return "Nutrition analysis completed. Detailed implementation pending."
            
        except Exception as e:
            return f"Error in nutrition analysis: {str(e)}"

## Creating Exercise Planning Tool
class ExerciseToolInput(BaseModel):
    """Input schema for ExerciseTool."""
    blood_report_data: str = Field(description="Blood test report data for exercise planning")

class ExerciseTool(BaseTool):
    name: str = "Create Exercise Plan from Blood Report"
    description: str = "Create personalized exercise recommendations based on blood report data"
    args_schema: Type[BaseModel] = ExerciseToolInput
    
    def _run(self, blood_report_data: str) -> str:
        """Create personalized exercise recommendations based on blood report data.
        
        Args:
            blood_report_data (str): Blood test report data
            
        Returns:
            str: Exercise plan recommendations based on health markers
        """
        try:
            if not blood_report_data or not blood_report_data.strip():
                return "Error: No blood report data provided for exercise planning"
                
            # TODO: Implement comprehensive exercise planning logic here
            # This would include analyzing:
            # - Cardiovascular markers
            # - Metabolic indicators
            # - Inflammatory markers
            # - Energy metabolism markers
            
            return "Exercise plan created. Detailed implementation pending."
            
        except Exception as e:
            return f"Error in exercise planning: {str(e)}"