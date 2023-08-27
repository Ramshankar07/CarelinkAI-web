import streamlit as st
import speech_recognition as sr
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import pyaudio
# from elevenlabs import generate

PAT = '5881bd40da7a40c08e8d3c0faa1c4aee'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'dj7fu4s80fz1'
XI_API_KEY = "adece68de32121faed9c205107d415d1"

APP_ID = 'Sentiment-analysis-1'
# Change these to whatever model and text URL you want to use
WORKFLOW_ID = 'workflow-c2d009'

st.title("CareLinkAI Web")
st.write("Smart AI-Driven Solutions for Telecom Operation and Customer Support")


start_button = st.button("Start Conversation")
stop_button = st.button("End Conversation")
st.write("\n\n\n")
recognized_text = ""
st.write("How can I assist you today?")

if start_button:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("Listening..."):
            audio = r.listen(source)
            try:
                recognized_text = r.recognize_google(audio).lower()
                st.write(f"Customer: {recognized_text}")
            except sr.UnknownValueError:
                st.write("Sorry, Can you please rephrase that?")
            except sr.RequestError as e:
                st.write(f"Could not retrieve results. {e}")
if stop_button:
    # st.write(f"Conversation Ended : Recognized Text: {recognized_text}")


# if name == "main":
#     main()

    TEXT = "Context: airkom is a telecommunication company that offers ,Question: "+recognized_text+" ,Instructions: Please provide a detailed and accurate response to the customers inquiry, using the information provided in the context and any additional knowledge you may have about telecommunication company and its products/services. Desired response: A clear and concise answer to the customers inquiry, including any relevant information or suggestions."

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)
    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    post_workflow_results_response = stub.PostWorkflowResults(
				service_pb2.PostWorkflowResultsRequest(
					user_app_id=userDataObject,  
					workflow_id=WORKFLOW_ID,
					inputs=[
						resources_pb2.Input(
							data=resources_pb2.Data(
								text=resources_pb2.Text( 
							raw= TEXT)
						)
				)]
				),
				metadata=metadata
			)
    if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
            print(post_workflow_results_response.status)
            raise Exception("Post workflow results failed, status: " + post_workflow_results_response.status.description)

			# We'll get one WorkflowResult for each input we used above. Because of one input, we have here one WorkflowResult
    results = post_workflow_results_response.results[0]

			# Each model we have in the workflow will produce one output.
    for output in results.outputs:
        model = output.model
    # print("Predicted concepts for the model `%s`" % model.id)
    for concept in output.data.concepts:
        print("	%s %.2f" % (concept.name, concept.value))

			# Uncomment this line to print the full Response JSON
    # print(results)
    last_raw = None
    for item in results['inputs'][::]:
        if 'raw' in item:
            last_raw = item['raw']['raw']

    # json_obj['data']['text']['ai-out']
    st.write(f"Agent : {last_raw}")
# audio = generate(text=results,
# 						voice="Arnold",
# 						model='eleven_monolingual_v1',
# 						api_key= XI_API_KEY )
