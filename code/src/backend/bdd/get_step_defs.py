import re
from bdd import generate_bdd
import os
import subprocess
from bdd import check_bdd
import time
from bdd import check_step_def
from typing import Set
from utils.extract_gherkin import extract_gherkin_scenarios

STEP_DEFINITIONS_DIR = "features/steps"
STEP_DEFINITIONS_FILE = "catfact_steps.py"
FEATURES_DIR = "features"
FEATURE_FILE = "catfact.feature"
RANDOM_STRING = "ahdG2kLdXydsauih"

global_step_registry = set()

def generate_prompt(bdd, endpointStr, base_url, api_schema):
    return f"""Generate Python Behave step definitions for the following Gherkin BDD feature:

    {bdd}

API URL: {base_url}
endpoints: {endpointStr}
API Schema: {api_schema}
The output should be a complete Python script with appropriate Behave step definitions, including necessary imports and structured functions. Each function should be decorated with the corresponding Gherkin keyword (e.g., @given, @when, @then). Write the script inside triple ` backticks.

    """

def read_bdd_from_file():
    """
    Reads the BDD syntax from the catfact.feature file.
    """
    try:
        with open(os.path.join(FEATURES_DIR, FEATURE_FILE), "r") as file:
            bdd_content = file.read()
            print("Loaded BDD Syntax:")
            print(bdd_content)
            return bdd_content
    except Exception as e:
        print(f"Error reading BDD file: {str(e)}")
        return ""

def update_bdd_file(corrected_bdd: str, feature_dir: str, feature_file_name: str):
    """
    Updates the catfact.feature file with the corrected BDD syntax.
    """
    try:
        os.makedirs(feature_dir, exist_ok=True)
        with open(feature_file_name, "w") as file:
            file.write(corrected_bdd)
            print("✅ BDD syntax updated successfully!")
    except Exception as e:
        print(f"Error updating BDD file: {str(e)}")


def extract_step_definitions(response_text: str) -> str:
    """
    Extracts the step definitions enclosed within triple quotes (''' ''') from the response text.

    Args:
        response_text (str): The raw response text from the LLM.

    Returns:
        str: The extracted step definitions or a message if no definitions are found.
    """
    try:
        # Regular expression to capture text between triple quotes (''' ''')
        pattern = r"```(?:\w*)?\n(.*?)```"
        matches = re.findall(pattern, response_text, re.DOTALL)

        # if not matches:
        #     pattern = r"```(.*?)```"
        #     matches = re.findall(pattern, response_text, re.DOTALL)

        if matches:
            step_definitions = matches[0]  # Taking the first occurrence of triple-quoted code
            print("Extracted Step Definitions:")
            print(step_definitions)
            return step_definitions
        else:
            print("No step definitions found inside triple quotes.")
            return ""

    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return ""

def normalize_step_text(step_text: str) -> str:
    """
    Normalize step text by removing extra spaces and making it lowercase.
    """
    return " ".join(step_text.lower().split())

def load_existing_steps(step_file_name: str):
    """
    Load existing steps from the given step definition file into the global step registry.
    """
    global global_step_registry
    try:
        if os.path.exists(step_file_name):
            with open(step_file_name, "r") as file:
                content = file.read()
                # Regular expression to match @given, @when, and @then steps
                step_pattern = r'@(given|when|then)\("([^"]+)"\)'
                existing_steps = set(re.findall(step_pattern, content, re.IGNORECASE))
                # Normalize and add existing steps to the global registry
                for step_type, step_text in existing_steps:
                    normalized_text = normalize_step_text(step_text)
                    step_key = (step_type.lower(), normalized_text)
                    global_step_registry.add(step_key)
    except Exception as e:
        print(f"Error loading existing steps from file {step_file_name}: {str(e)}")

def update_step_definitions(step_content: str, step_file_name: str):
    """
    Updates the step definition file with new step definitions.
    Appends to the file if the step title is unique globally.
    """
    try:
        # Load existing steps from the file only once
        load_existing_steps(step_file_name)

        # Regular expression to match @given, @when, and @then steps
        step_pattern = r'@(given|when|then)\("([^"]+)"\)'

        # Extract new step titles from the content
        new_steps = re.findall(step_pattern, step_content, re.IGNORECASE)

        # Check for duplicate steps and filter them out
        unique_steps = []
        for step_type, step_text in new_steps:
            normalized_text = normalize_step_text(step_text)
            step_key = (step_type.lower(), normalized_text)
            if step_key not in global_step_registry:
                unique_steps.append((step_type, step_text))
                global_step_registry.add(step_key)  # Update the global set

        # If there are unique steps, append them to the file
        if unique_steps:
            with open(step_file_name, "a") as file:
                file.write("\n" + step_content)
                print(f"✅ Step definitions updated successfully at: {step_file_name}")
        else:
            print(f"⚠️ No unique step definitions to add.")
            
    except Exception as e:
        print(f"Error updating step definitions file: {str(e)}")


def save_step_definitions(step_definitions: str, step_def_dir, step_def_file_name):
    """
    Saves the generated step definitions to the correct file.
    """
    try:
        os.makedirs(step_def_dir, exist_ok=True)

        with open(step_def_file_name, "w") as file:
            file.write(step_definitions)
            print(f"Step definitions saved to: {step_def_file_name}")

    except Exception as e:
        print(f"Error saving step definitions: {str(e)}")

def process_bdd(bdd: str) -> str:
    """
    Calls the LLaMA model to check the BDD syntax and update it if needed.
    """
    print("🧐 Checking BDD Syntax...")
    validation_result = check_bdd.check_gherkin_syntax(bdd)

    # If the response is the random string, it means syntax is correct
    if RANDOM_STRING in validation_result:
        print("✅ BDD syntax is correct!")
        return [bdd]

    # If syntax is incorrect, extract the corrected syntax from the response
    print("❌ BDD syntax is incorrect. Updating...")
    bdd_list = extract_gherkin_scenarios(bdd)
    if bdd_list==[]:
        return [bdd]
    # corrected_syntax_pattern = r"```(?:\w*)?\n(.*?)```"
    # matches = re.findall(corrected_syntax_pattern, validation_result, re.DOTALL)
    # if not matches:
    #     corrected_syntax_pattern = r"```(.*?)```"
    #     matches = re.findall(corrected_syntax_pattern, validation_result, re.DOTALL)
    # if matches:
    #     corrected_bdd = matches[0].strip()
    #     print("✅ Corrected BDD syntax extracted.")
    #     print(corrected_bdd)
    #     return corrected_bdd
    # else:
    #     print("❌ Failed to extract corrected BDD syntax from the response.")
    #     return bdd

def process_step_def(bdd: str, step_def: str, api_schema: str) -> str:
    validation_result = check_step_def.check_step_def(bdd, step_def, api_schema)

    if RANDOM_STRING in validation_result:
        print("✅ Step Definition is correct!")
        return step_def
    corrected_syntax_pattern = r"```(?:\w*)?\n(.*?)```"
    matches = re.findall(corrected_syntax_pattern, validation_result, re.DOTALL)
    # if not matches:
    #     corrected_syntax_pattern = r"```(.*?)```"
    #     matches = re.findall(corrected_syntax_pattern, validation_result, re.DOTALL)
    if matches:
        corrected_step_def = matches[0].strip()
        print("✅ Corrected Step Definition extracted.")
        print(corrected_step_def)
        return corrected_step_def
    else:
        print("❌ Failed to extract corrected Step Definition from the response.")
        return step_def

def run_behave_tests(features_dir, reports_dir):
    """
    Runs the Behave tests.
    """
    try:
        print("\nRunning Behave tests...")
        html_dir = f"{reports_dir}/html"
        command = ["behave", features_dir, "--no-capture-stderr", "-f", "allure_behave.formatter:AllureFormatter", "-o", reports_dir]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ All tests passed successfully!")
        else:
            print("❌ Some tests failed.")
            print(result.stderr)
        print(f"Generating Allure HTML report...")
        generate_command = ["allure", "generate", reports_dir, "-o", html_dir, "--clean"]
        result = subprocess.run(generate_command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"HTML report generated successfully!")
            return True
        else:
            print(f"Failed to generate HTML report:")
            print(result.stdout)
            print(result.stderr)
            return False
        
    except Exception as e:
        print(f"Error while running Behave tests: {str(e)}")


def get_step_defs(BDDs, base_url, endpoints, application_name, api_schema):
    feature_dir = f"bdd/{application_name}/features/"
    steps_dir = f"{feature_dir}steps/"
    steps_file_name = f"{steps_dir}{application_name}_steps.py"
    reports_dir = f"reports/{application_name}"
    endpoints_string = "\n".join(endpoints)
    test_cases_success = True
    for i, bdd in enumerate(BDDs):
        feature_file_name = f"{feature_dir}{application_name}_{i}.feature"
        bdd_list = process_bdd(bdd)
        for final_bdd in bdd_list:
            update_bdd_file(final_bdd, feature_dir, feature_file_name)
            prompt = generate_prompt(bdd=final_bdd, base_url=base_url, endpointStr=endpoints_string, api_schema=api_schema)
            print("Calling Prompt...", prompt)
            response_text = generate_bdd.generate_bdd(prompt)
            # print("Generated Response Text:", response_text)
            step_defs = extract_step_definitions(response_text)
            step_defs = process_step_def(final_bdd, step_defs, api_schema)
            save_step_definitions(step_definitions=step_defs, step_def_dir=steps_dir, step_def_file_name=steps_file_name)
            if not run_behave_tests(feature_file_name, reports_dir):
                test_cases_success = False
        # update_step_definitions(step_content=step_defs,step_file_name=steps_file_name)
    return test_cases_success





# BDD = read_bdd_from_file()

# # Check and update BDD syntax if necessary
# BDD = process_bdd(BDD)

# time.sleep(10)

# response_text = generate_bdd.generate_bdd("""Generate Python Behave step definitions for the following Gherkin BDD feature:

#     {BDD}

# API URL: http://192.168.1.5:9000/
# The output should be a complete Python script with appropriate Behave step definitions, including necessary imports and structured functions. Each function should be decorated with the corresponding Gherkin keyword (e.g., @given, @when, @then). Write the script inside triple ` backticks.

#     """)


# # print(response_text)

# # # Extract the step definitions from the response text
# extracted_steps = extract_step_definitions(response_text)
# time.sleep(10)
# extracted_steps = process_step_def(BDD, extracted_steps)
# save_step_definitions(extracted_steps)
# run_behave_tests()
#behave --format allure_behave.formatter:AllureFormatter -o "reports"   




