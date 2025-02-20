import os, re
import streamlit as st
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
import prompt_templates

# Load OpenAI API key from environment variable
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI API client
client = OpenAI()

assistant = client.beta.assistants.create(
    name="TasOn Assistant",
    instructions=prompt_templates.assistant_system_prompt,
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

# Check if vector store exists, if not create one
vector_store_path = "src/vector_stores/financial_statements_store_id.txt"

if os.path.exists(vector_store_path):
    with open(vector_store_path, "r") as file:
        vector_store_id = file.read().strip()
    vector_store = client.beta.vector_stores.retrieve(vector_store_id)
else:
    vector_store = client.beta.vector_stores.create(name="Financial Statements")
    with open(vector_store_path, "w") as file:
        file.write(vector_store.id)

# Ready the files for upload to OpenAI
file_paths = ["data/tma_landing_page.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Create a thread and attach the file to the message
def create_thread_with_file(client, query):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ]
    )
    return thread

# Main function to run the Streamlit app
def main():
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content":prompt_templates.greeting_prompt}]
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User-provided prompt
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="data/tason_icon.png"):
            st.write(prompt)
            
    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("답변을 준비 중입니다..."):
                thread = create_thread_with_file(client, prompt)
                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id, assistant_id=assistant.id
                )

                messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

                response = messages[0].content[0].text.value
                # annotation 제거(임시방편)
                pattern = r'【.*pdf】'
                cleaned_response = re.sub(pattern, '', response)

                st.write(cleaned_response) 
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
if __name__ == "__main__":
    main()
