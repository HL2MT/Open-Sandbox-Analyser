import os
import json  # For parsing the JSON response
import google.generativeai as genai
import re
import streamlit as st
from git import Repo

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "gemini Api Key"  # Replace with your actual API key file path  link: https://aistudio.google.com/app/prompts/new_chat?gad_source=1&gclid=Cj0KCQjwpvK4BhDUARIsADHt9sRAYLFVfLEwMG-Yz5wwJ6p3JozW8DB2hK-eqmP9uYOLJ12Qw8vNheAaAq4pEALw_wcB
genai.configure(api_key=os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')

def clone_repository(repo_url, local_path):
    """Clone a GitHub repository to a local directory."""
    Repo.clone_from(repo_url, local_path)
 #   st.success(f"Repository cloned to {local_path}")

def get_file_structure(repo_path):
    """Generate a structured representation of the repository."""
    structure = []
    for root, dirs, files in os.walk(repo_path):
        level = root.replace(repo_path, '').count(os.sep)
        indent = '  ' * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        for file in files:
            structure.append(f"{indent}  {file}")
    return '\n'.join(structure)

def get_file_content_summary(file_path):
    """Read and return a summary of the file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return f"File content summary:\n{content[:1000]}..." if len(content) > 1000 else content
    except UnicodeDecodeError:
        return "[Binary file]"


def analyze_repository_workflow(repo_path):
    """Generate a workflow analysis for the repository."""
    structure = get_file_structure(repo_path)

    file_summaries = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_path)
            summary = get_file_content_summary(file_path)
            file_summaries.append(f"File: {relative_path}\n{summary}\n")

    prompt = f"""Analyze the following GitHub repository structure and provide a detailed functional analysis:
    Repository Structure:
    {structure}

    File Summaries:
    {''.join(file_summaries)}

    Please provide:
    1. A detailed description of the repository's workflow, including how the whole repo works from one end to final end and how data or control flows between different components.
    2. A complete and detailed workflow analysis with all the conditions included in repo.
    3. Every process or operation that occurs within the system.
    4. Any important decision points or conditional flows in the system.
    5. Each and every functionality present in the repo. For important functionalities use high level and for common functionality use low level. Don't miss even a single functionality in repo, give as much as you can.

    For each functionality, use the  json with following format:
    FUNCTIONALITY: [Name of functionality]
    DESCRIPTION: [Description of functionality]
    LEVEL: [High level/Low level]
    USAGE: [How and where it is used]
    BASE_DIRECTORY: [Base directory of the functionality]
    USED_IN: [file1.py, file2.py]
    DEFINED_IN: [file3.py, file4.py]


    """

    try:
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return "Analysis blocked due to content safety measures. Please check the repository content."
    except Exception as e:
        return f"Error during analysis: {str(e)}"

def functionality_extractor(repository_analysis):
  fucn={}

  for i in range(1,len(repository_analysis.split("FUNCTIONALITY:"))):
    fucn[repository_analysis.split("FUNCTIONALITY:")[i].split("\n")[0]]=repository_analysis.split("FUNCTIONALITY:")[i].split("\n")[1:]
  #print(analyze_repository.split("FUNCTIONALITY:")[i].split("\n")[:])

  import re
  import json
  int_fucn={}
  for key,value in fucn.items():
    new_dictionary={}
    for val in value:
      if "DESCRIPTION" in val:
        new_val=val.split(":")[:]
        new_dictionary[re.sub(r'[^a-zA-Z0-9,/_\-\.]', '', new_val[0])]= new_val[1:]
      elif "BASE_DIRECTORY" in val:
        bs_val=val.split(":")[:]
        new_vl=[]
        for itm in bs_val[1:]:
          new_vl.append(re.sub(r'[^a-zA-Z0-9,/_\-\.]', '', itm))
        print(new_vl)


        new_dictionary[re.sub(r'[^a-zA-Z0-9,/_\-\.]', '', bs_val[0])]=  new_vl
    int_fucn[re.sub(r'[^a-zA-Z0-9,/_\-\.]', '', key)]=new_dictionary
    return int_fucn
    #output_file='output.json'
    #with open(output_file, 'w', encoding='utf-8') as outfile:
      #json.dump(int_fucn, outfile)
  print(int_fucn)

def main():
    st.title("GitHub Repository Analyzer")

    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    #repo_url = st.text_input("Enter the GitHub repository URL:")
    #local_directory=st.text_input("Enter_where you want to store repo")
    #local_path = f"./{local_directory}"
    local_path="codium_cover_agent"

    if st.button("Analyze Repository"):
        with st.spinner("Cloning and analyzing repository..."):
            #clone_repository(repo_url, local_path)
            st.session_state.analysis_results = analyze_repository_workflow(local_path)
        st.success("Analysis complete!")
        functionality_extractor(st.session_state.analysis_results)
        if st.session_state.analysis_results:
            st.write(st.session_state.analysis_results)



if __name__ == "__main__":
    main()

