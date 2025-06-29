# Project Setup and Execution Guide

## Getting Started

### Install Required Libraries
```sh
pip install -r requirement.txt
```
### Add .env file
```sh
GEMINI_API_KEY=
DATABASE_URL=sqlite:///./blood_test_analyzer.db
```

### Run the server
```sh
python main.py
```
### API Documentation
http://localhost:8000/docs  
(after executing the program)

### Testing
You can use **Postman** or **Thunder CLient in VSCode**. Set methods as per need, provide required URL and set body and then hit "Send".  

**Example:**  
Method: POST  
URL: localhost:8000/analyze  
Body->form-data

|Key|Type|Value|
|---|----|-----|
file|File| sample.pdf
query|Text| Analyze my blood test and give me health recommendations
analysis_type|Text|comprehensive
user_uuid|Text|Leave empty for anonymous user  

You can set 'analysis_type' as: comprehensive, medical, nutrition, exercise, verification

Sample output: https://gist.github.com/scoder17/ca7565967067dca38ec2a7913ef27b2c  



# You're All ~Not~ Set!
🐛 **Debug Mode ~Activated~ Deactivated!** The project ~has~ had bugs waiting to be squashed - your mission ~is~ was to fix them and bring it to life.

---

## 🐛 Bug Fix Summary: `requirements.txt`

| Issue | Description | Fix |
|-------|-------------|-----|
Lots of packages were conflicting with each other |First I started with fixing each conflict one by one, but i was struck in a deadlock because of so many conflicts, thus deleted reqirements.txt| Started with installation as per requirement. I started with installing crewai==0.130.0 and followed further.| nothing

## 🐛 Bug Fix Summary: `agents.py`

| Issue | Description | Fix |
|-------|-------------|-----|
| **1. Undefined LLM object** | The original file tried to assign `llm = llm`, causing a `NameError`. | Explicitly initialized `llm` using the `LLM` class with a valid model (`gemini/gemini-2.0-flash`). |
| **2. Dangerous and unethical agent behavior** | Agents (especially doctor, verifier, nutritionist, and exercise specialist) were given irresponsible, unsafe, or even deliberately wrong roles and goals. | Rewritten agent roles, goals, and backstories to follow professional, ethical, and evidence-based practices. |
| **3. Misuse of humor and satire in critical roles** | The backstories were written for satire/comedy (e.g., Dr. House-like behavior, CrossFit fanaticism, Instagram nutritionist, etc.). This posed a serious risk in a medical context. | Updated all backstories with realistic and professional medical/scientific profiles to ensure safety and credibility. |
| **4. Incorrect use of `tool` vs `tools`** | Used `tool=[...]` instead of the correct keyword `tools=[...]` as expected by the `Agent` constructor. | Corrected to use `tools=[BloodTestReportTool()]`. |
| **5. Agents lacked proper boundaries on iteration and rate limits** | All agents were limited to `max_iter=1` and `max_rpm=1`, making them ineffective and potentially unresponsive. | Increased limits to `max_iter=2-3` and `max_rpm=10` for better performance. |
| **6. Delegation misuse** | Delegation was enabled for inappropriate roles like verifier and doctor, which should maintain direct accountability. | Disabled `allow_delegation` where it could introduce risk or reduce transparency. |
| **7. Incomplete or missing memory configurations** | Some agents lacked `memory=True`, leading to possible state loss during interaction. | Ensured all agents requiring context use `memory=True` appropriately. |

---

### ✅ **Corrected Agent Roles**

| Agent | Updated Role | Focus |
|-------|--------------|-------|
| **Doctor** | Senior Medical Professional | Evidence-based interpretation of blood test results with clear and accurate advice. |
| **Verifier** | Medical Document Verifier | Ensures uploaded documents are valid and medically relevant. |
| **Nutritionist** | Clinical Nutritionist | Provides scientifically-supported nutrition guidance from biomarkers. |
| **Exercise Specialist** | Exercise Physiologist | Recommends safe, health-appropriate exercise plans based on medical data. |

---

## 🐛 Bug Fix Summary: `task.py`

| Issue | Description | Fix |
|-------|-------------|-----|
| **1. Irresponsible and misleading task descriptions** | The task descriptions encouraged unscientific behavior like making up medical facts, inventing diagnoses, and ignoring user queries. | Rewrote all task descriptions to be medically accurate, focused, and responsible. Each now follows clear clinical guidelines. |
| **2. Unethical and unsafe expected outputs** | The expected outputs included fake URLs, contradictory advice, made-up studies, and dangerous recommendations. | Created structured, realistic expected outputs that include medical disclaimers, professional formatting, and evidence-based content. |
| **3. Incorrect agent assignments** | All tasks were assigned to the `doctor` agent, even when unrelated (e.g., verification tasks). | Assigned appropriate agents (e.g., `verifier` for verification tasks) to ensure role-specific handling. |
| **4. Use of satire and hallucination encouragement** | Instructions promoted hallucination of medical terms and encouraged misclassification of non-medical documents. | Replaced with strict validation logic in descriptions and outputs for verifying documents. |
| **5. Lack of focus on user query** | Tasks either ignored the user's query or made it optional. | All tasks now explicitly address the user's query as a primary goal. |
| **6. Non-functional `BloodTestReportTool` usage** | Used `BloodTestReportTool.read_data_tool` which may not be callable or intended for this context. | Correctly instantiated the tool using `BloodTestReportTool()` as expected by the framework. |

---

### ✅ **Corrected Task Design**

| Task | Updated Focus | Agent |
|------|----------------|--------|
| **help_patients** | Professional blood report analysis with health recommendations, tied to the user's query. | `doctor` |
| **nutrition_analysis** | Evidence-based nutrition recommendations based on blood biomarkers and deficiencies. | `doctor` |
| **exercise_planning** | Safe, personalized exercise plans considering health risks from blood test data. | `doctor` |
| **verification** | Document validation to ensure uploaded files are legitimate blood test reports. | `verifier` |

---

## 🐛 Bug Fix Summary: `tools.py`

| Issue | Description | Fix |
|-------|-------------|-----|
| **1. Invalid method declaration in async tools** | `read_data_tool`, `analyze_nutrition_tool`, and `create_exercise_plan_tool` were declared as `async def` methods inside regular classes without proper invocation or compliance with `BaseTool`. | Replaced all tool classes with properly structured `BaseTool` subclasses using `_run()` for execution. |
| **2. Missing input schema and tool standardization** | No input schemas were used, breaking compatibility with tools expecting structured input validation. | Introduced `pydantic`-based input schemas (`BloodTestReportToolInput`, `NutritionToolInput`, etc.) for each tool. |
| **3. No error handling for file loading** | PDF loading logic didn’t check for file existence or handle errors gracefully. | Added error checks for file existence, content emptiness, and exception catching with user-friendly messages. |
| **4. Incorrect use of unimported modules** | The `PDFLoader` class was referenced but never imported, causing runtime errors. | Correctly imported `PyPDFLoader` from `langchain_community.document_loaders`. |
| **5. Ineffective data cleaning logic** | Manual string manipulation (e.g., removing double spaces) was inefficient and unstructured. | Replaced with consistent `str.replace()` and `.strip()` operations for better formatting. |
| **6. No return handling for empty or missing data** | Tools did not check if blood report data was empty or invalid. | Added validations to return appropriate error messages if no data is available or passed. |
| **7. No real integration with CrewAI tooling framework** | Tools were raw methods and didn’t conform to CrewAI’s `BaseTool` interface. | All tools were refactored as proper `BaseTool` subclasses with `name`, `description`, `args_schema`, and `_run()` logic. |

---

### ✅ **Corrected Tool Designs**

| Tool | Updated Class | Description |
|------|---------------|-------------|
| **PDF Reader** | `BloodTestReportTool` | Loads and cleans blood test PDF data, includes file existence checks and robust formatting. |
| **Nutrition Analyzer** | `NutritionTool` | Accepts blood report data, returns structured placeholder for future nutrition insights. |
| **Exercise Planner** | `ExerciseTool` | Generates safe exercise guidance based on blood markers (pending full implementation). |

---

## 🐛 Bug Fix Summary: `main.py`

| Issue | Description | Fix |
|-------|-------------|-----|
| **1. Missing file type validation** | Users could upload non-PDF files (e.g., `.jpg`, `.txt`) without restriction. | Added strict file type validation to only accept `.pdf` files with a proper HTTP 400 error on invalid input. |
| **2. Incomplete variable passing to Crew kickoff** | The `file_path` argument was defined in `run_crew` but never passed to `kickoff()`, making the file unusable during task execution. | Added `'file_path': file_path` to the dictionary passed to `kickoff()` for proper downstream usage. |
| **3. Poor result formatting** | Returned `str(response)` which may not provide structured output. | Used `str(response.raw)` to return meaningful analysis content. |
| **4. Inefficient query validation** | Checked `query=="" or query is None`, which is verbose and error-prone. | Replaced with `if not query or query.strip() == ""` for more concise and reliable validation. |
| **5. Redundant `reload=True` in `uvicorn.run()`** | Running with `reload=True` in production mode is unnecessary and unsafe. | Removed `reload=True` to ensure consistent deployment behavior. |
| **6. No file extension check before saving** | Files were saved and processed without checking if the extension matched expectations. | Added a file extension check before proceeding with save and analysis logic. |

---

### ✅ **Corrected API Behavior**

| Endpoint | Description | Improvements |
|----------|-------------|--------------|
| `GET /` | Health check endpoint | ✔️ Unchanged and functional |
| `POST /analyze` | Uploads and analyzes blood report PDFs | ✔️ Now checks file type, securely saves uploads, runs full crew analysis, and returns clean structured output |

---

# Bonus Points

-  Database Integration: Add database for storing analysis results and user data  
   Used SQLite using SQLAlchemy