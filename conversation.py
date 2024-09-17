import pandas as pd


# To pass the messages
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage


from output_formatting import convert_to_json
from script_execution_and_check import check_and_fix_script
from script_execution_and_check import invoke_tool_with_capture





# Example use in the begin_conversation function
def begin_conversation(question, chain, chat_history, llm,local_vars):
    initial_response = chain.invoke({"question": question, "chat_history": chat_history})
    initial_content = initial_response.content
    
    information = convert_to_json(initial_content)
    script = information.get('Script')
    error_details = []
    solution = None

    if script is not None:
        fixed_script, error_details = check_and_fix_script(script, local_vars,llm,fix_count=3)
        information['Error Details'] = error_details
        if fixed_script:
            # Use the custom function to capture all output from the script
            solution,local_vars = invoke_tool_with_capture(fixed_script,local_vars)
            information['Solution'] = solution

    if solution is not None:
        enriched_question = (
            f"The tool has provided the following solution based on your question: {question}:\n\n"
            f"{solution}\n\n"
            f"Please use this information to while answering the question."
        )

        # print("Enriched Question:", enriched_question)
        # print("Chat History:\n",chat_history)

        final_response = chain.invoke({"question": enriched_question, "chat_history": chat_history})
        final_content = final_response.content
    else:
        final_content = initial_content
    
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=final_content))
    
    total_information = {
        "question": question,
        "content": initial_content,
        "information": information,
        "solution": solution,
        "final_answer":final_content
    }
    
    return chat_history, total_information


def run_conversation(question,chain,llm,total_information_bucket,chat_history_bucket,local_vars):
    
    chat_history, total_information = begin_conversation(question, chain, chat_history_bucket, llm, local_vars)

    chat_history_bucket = chat_history
    total_information_bucket.append(total_information)

    # return total_information_bucket,chat_history_bucket
    return total_information_bucket,chat_history[-2:]
