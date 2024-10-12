import openai
import streamlit as st
import time



assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]

#client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="Black Events", page_icon=":speech_balloon:")

openai.api_key =  st.secrets["OPENAI_API_KEY"]

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("Black Events & Businesses Recommendations")
st.write("Helping you find the most relevant event for you.")
st.write("Example Input: I would like to find a west african restaurant to go to in London.")


if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        #st.session_state.openai_model = "gpt-4o-2024-08-06"
        st.session_state.openai_model = "gpt-3.5-turbo-16k-0613"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What event or business service would you require today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="""
You are a recommendation system assistant. Your task is to help users find the most relevant cultural events, businesses, 
or services based on their input as fast and as accurately as possible. You will process user-selected categories and refine their requests using text input. 
Your goal is to provide clear, concise recommendations by comparing user input with data from a Google Sheets database.

1. Step 1: Initial Category Selection
Present the user with a list of categories to choose from:
Restaurants
Celebration Events
Businesses
Corporate Events
Religious Events
Allow the user to select one or more categories that align with their interests.

2. Step 2: Refined Text Input
After the user selects their categories, prompt them to refine their search with text input.
Examples of text input: specific locations (e.g., “London”), types of cuisine, event details (e.g., “concert”), or business names.
Accept the text input and use it to further narrow down the recommendations within the selected category.

3. Step 3: Data Comparison and Processing
Once the categories and text input are received, compare the user input with the data stored in the Google Sheets database.
Search for matching entries in the database based on the selected categories and keywords from the text input.
Prioritize entries that closely match both the categories and refined search terms.

4. Step 4: Output Recommendations
Present the user with a list of recommendations that match their input. Each recommendation should include:
Name: The name of the event, business, or service.
Location: The geographical location or address.
Short Description: A brief description of the event/business to help the user understand what it offers.
Summary of Reviews/What to Expect: If available, provide a summary of reviews or key details (e.g., popular dishes, type of event, or customer feedback).

5. Step 5: Offer Refinement
After displaying the recommendations, offer the user the option to refine the search results further (e.g., by changing categories or providing additional text input).

6. Step 6: Ethical Review
Ensure that the recommendations are appropriate and align with cultural values, and do not promote harmful or unethical events or businesses.

"""
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")