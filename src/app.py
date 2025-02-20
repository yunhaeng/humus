import os, re
import streamlit as st
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
import prompt_templates
from dotenv import load_dotenv
import html

# Load OpenAI API key from environment variable
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

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

def message_func(text, is_user=False):
    """
    This function displays messages in the chatbot UI, ensuring proper alignment and avatar positioning.

    Parameters:
    text (str): The text to be displayed.
    is_user (bool): Whether the message is from the user or not.
    """
    user_icon_url = "https://qoqikkpcsdeczpaorova.supabase.co/storage/v1/object/public/snowchat/cat-with-sunglasses.png?t=2024-05-07T21%3A17%3A21.951Z"
    bot_icon_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAMFBMVEVHcEwAZTsAZTsAaz0AZjsAZjwAZjwAZTv///8AWiYAVBvZ6eJHimszgF7Y6OHi7enhJ15mAAAAB3RSTlMA0JAT6qJMk96vsAAAALhJREFUOI2Nk9ESxBAMRYmQZWn//2+XnRYRqnf60EnOcCOJUk0ONBKhBqcmMpY6WTPmgQYBz+sxT6T742W6qF0zzxM9nM9uEf4GpwsDzcZdf2C6grY5DB+mVH26ORCvsKsWFwC0GlOMMZ3l9Pxz53Ol2JsORwZCH0H+iv6bAc9CewCfAeSNkIDmnZAA1IdaAI4PgwS6Zk0BO7RbAGYYGH9wAMTI+f/Xanw5tPux3y7Oi9XbL2/RdP1/WhgW484KQnwAAAAASUVORK5CYII="
    avatar_url = user_icon_url if is_user else bot_icon_url
    message_bg_color = (
        "#EFF6F8" if is_user else "#0FD07E"
    )
    avatar_class = "user-avatar" if is_user else "bot-avatar"
    alignment = "flex-end" if is_user else "flex-start"
    margin_side = "margin-left" if is_user else "margin-right"

    if text:  # Check if message_text is not empty
        #프로필 포함 html
        if is_user:
            container_html = f"""
            <div style="display:flex; align-items:flex-start; justify-content:flex-end; margin:0; padding:0; margin-bottom:10px;">
                <div style="background:{message_bg_color}; color:black; border-radius:20px; padding:10px; margin-right:5px; max-width:75%; font-size:20px; margin:0; line-height:1.2; word-wrap:break-word;">
                    {text}
                </div>
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width:40px; height:40px; margin:0;" />
            </div>
            """
        else:
            container_html = f"""
            <div style="display:flex; align-items:flex-start; justify-content:flex-start; margin:0; padding:0; margin-bottom:10px;">
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width:30px; height:30px; margin:0; margin-right:5px; margin-top:5px;" />
                <div style="background:{message_bg_color}; color:white; border-radius:20px; padding:10px; margin-left:5px; max-width:75%; font-size:20px; margin:0; line-height:1.2; word-wrap:break-word;">
                    {text}
                </div>
            </div>
            """

        #프로필 미포함 html
        # if is_user:
        #     container_html = f"""
        #     <div style="display:flex; align-items:flex-start; justify-content:flex-end; margin:0; padding:0; margin-bottom:10px;">
        #         <div style="background:{message_bg_color}; color:black; border-radius:20px; padding:10px; margin-right:5px; max-width:75%; font-size:20px; margin:0; line-height:1.2; word-wrap:break-word;">
        #             {text}
        #         </div>
        #     </div>
        #     """
        # else:
        #     container_html = f"""
        #     <div style="display:flex; align-items:flex-start; justify-content:flex-start; margin:0; padding:0; margin-bottom:10px;">
        #         <div style="background:{message_bg_color}; color:white; border-radius:20px; padding:10px; margin-left:5px; max-width:75%; font-size:20px; margin:0; line-height:1.2; word-wrap:break-word;">
        #             {text}
        #         </div>
        #     </div>
        #     """
        st.write(container_html, unsafe_allow_html=True)

# Initialize OpenAI API client
client = OpenAI()

assistant = client.beta.assistants.create(
    name="TasOn Assistant",
    instructions=prompt_templates.assistant_system_prompt,
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

with open("src/vector_stores/vector_store_id.txt", "r") as f:
    vector_store_id = f.read()

assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
)
# Main function to run the Streamlit app
def main():
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content":prompt_templates.greeting_prompt}]

    thread = client.beta.threads.create()

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state["assistant_response_processed"] = False

    messages_to_display = st.session_state.messages.copy()

    for message in messages_to_display:
        message_func(
            message["content"],
            is_user=(message["role"] == "user"),
        )
    
    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
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

            message_func(cleaned_response, is_user=False)
        message = {"role": "assistant", "content": cleaned_response}
        st.session_state.messages.append(message)
if __name__ == "__main__":
    main()
