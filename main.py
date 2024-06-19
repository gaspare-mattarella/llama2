import urllib.request
import json
import os
import ssl
import streamlit as st

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
chat_history = []
#data = {'chat_history':chat_history, 'question':'hi'}
#body = str.encode(json.dumps(data))

url = 'https://space-gpt.westeurope.inference.ml.azure.com/score'
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = st.secrets['api_key']
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# The azureml-model-deployment header will force the request to go to a specific deployment.
# Remove this header to have the request observe the endpoint traffic rules
headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'space-gpt-1' }


st.logo('ecb-logo_RGB_SymbolOnly.png', link = '', icon_image = 'ecb-logo_RGB_SymbolOnly.png')
st.html("""
        <style>
        [alt=Logo] {
            height: 4rem;
                }
        </style>
            """)
    
    

st.title("SPACE-GPT")
st.subheader("An AI coding Assistant for SPACE")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    data = {"chat_history": chat_history, "question": prompt}
    body = str.encode(json.dumps(data))
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        result = str(json.loads(result)['answer'])
        chat_history.append(prompt)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        result_col = ":black[%s]"%result
        st.markdown(result_col,unsafe_allow_html= True,)
        st.session_state.messages.append({"role": "assistant", "content": result})