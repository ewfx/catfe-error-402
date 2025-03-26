import os, sys
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.extend([
    os.path.join(base_dir, "VectorDB"),
    os.path.join(base_dir, "LLMS")
])

from typing_extensions import TypedDict

from langgraph.graph import StateGraph

from pinecone_client import get_vector_store
from chatGroq import init_llm, init_llm2, init_llm3
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
import operator

from typing import List, Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from IPython.display import Image, display
from langchain.schema import Document
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver

vector_store = get_vector_store()
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Here we are initializing three LLM instances with different keys to avoid reaching the Token per minute(TPM)
# limit to the model
llm=init_llm()
llm2=init_llm2()
llm3=init_llm3()


from typing import Literal

class routerResult(BaseModel):
    source: Literal['websearch', 'vectorstore', 'chat_bot']

    
router_llm = llm.with_structured_output(routerResult)
answer_grader_llm = llm.with_structured_output(method='json_mode')

# Prompt
router_instructions = """You are an expert at routing a user question to a vectorstore, web search or chat_bot.

The vectorstore contains documents related to fraud detection api, personal project, my project, bdd tests,

confluence pages, JIRA tickets, github code , architecture diagrams, project functioning.

Use the vectorstore for questions on these topics. For else, use 'chat_bot' . Use 'websearch' if the question/

statement states to use latest data.

Return a single word 'websearch' or 'vectorstore' or 'chat_bot' depending on the question in JSON format."""



### Retrieval Grader

# Doc grader instructions
doc_grader_instructions = """You are a grader assessing relevance of a retrieved document to a user question.

If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant."""

# Grader prompt
doc_grader_prompt = """Here is the retrieved document: \n\n {document} \n\n Here is the user question: \n\n {question}. 

This carefully and objectively assess whether the document contains at least some information that is relevant to the question.

Return a single word that is 'yes' or 'no' score to indicate whether the document contains at least some information that is relevant to the question."""


### Generate

# Prompt
rag_prompt = """You are an assistant for question-answering tasks. 

Here is the context to use to answer the question:

{context} 

Think carefully about the above context. 

Now, review the user question:

{question}

Only if you need, use this conversation history also:

{conversation_history}

Provide an answer to this questions using the above context.   

Answer:"""

#removed only from Provide an answer to this questions using only the above context.   


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


### Hallucination Grader

# Hallucination grader instructions
hallucination_grader_instructions = """

You are evaluating answers related to our project.

You will be given a QUESTION and an ANSWER.

Here is the grading criteria:

(1) Ensure the ANSWER is relevant to the QUESTION.

(2) Ensure the ANSWER is accurate based on our project's requirements and constraints.

(3) Ensure the ANSWER does not introduce incorrect or misleading information.

Score:

- A score of 'yes' means the ANSWER meets all of the criteria.
- A score of 'no' means the ANSWER fails to meet at least one of the criteria.
"""

# Grader prompt
hallucination_grader_prompt = """Question: \n\n {documents} \n\n  ANSWER: {generation}. 

Return a single word 'yes' or 'no' score to indicate whether the  ANSWER meets the criteria"""


### Answer Grader

# Answer grader instructions
answer_grader_instructions = """You are evaluating answers related to our project.

You will be given a QUESTION and an ANSWER.

Here is the grading criteria:

(1) The ANSWER helps to address the QUESTION.

Score:

- A score of 'yes' means the ANSWER meets the criteria. This is the highest (best) score.  
- The ANSWER can receive a score of 'yes' even if it contains extra information not explicitly asked for in the QUESTION.  
- A score of 'no' means the ANSWER does not help to address the QUESTION. This is the lowest possible score.  

"""

# Grader prompt
answer_grader_prompt = """QUESTION: \n\n {question} \n\n  ANSWER: {generation}. 

Return a single word 'yes' or 'no' score to indicate whether the  ANSWER meets the criteria"""


web_search_tool = TavilySearchResults(k=3)



class GraphState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """

    question: str  # User question
    generation: str  # LLM generation
    web_search: str  # Binary decision to run web search
    max_retries: int  # Max number of retries for answer generation
    answers: int  # Number of answers generated
    loop_step: Annotated[int, operator.add]
    conversation_history: List[dict]
    documents: List[str]  # List of retrieved documents


### Nodes
def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Write retrieved documents to documents key in state
    documents = retriever.invoke(question)
    return {"documents": documents}


def generate(state):
    """
    Generate answer using RAG on retrieved documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state.get("documents",[])
    loop_step = state.get("loop_step", 0)
    conversation_history= state.get("conversation_history",[])

    print(conversation_history)

    # RAG generation
    docs_txt = format_docs(documents)
    rag_prompt_formatted = rag_prompt.format(context=docs_txt, question=question, conversation_history=conversation_history)
    generation = llm.invoke([HumanMessage(content=rag_prompt_formatted)])
    return {"generation": generation, "loop_step": loop_step + 1}


def chat_bot(state):
    """
    Generate answer as a chat bot

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    conversation_history= state.get("conversation_history",[])

    print(conversation_history)

    chat_bot_prompt="""You provide chat with ai service. Please respond to: {question} 
    If needed you can use this conversation_history: {conversation_history} if it is relevant"""
    updated_chat_bot_prompt=chat_bot_prompt.format(question=question, conversation_history=conversation_history)
    generation = llm2.invoke([HumanMessage(content=updated_chat_bot_prompt)])
    return {"generation": generation}

def store_history(state):
    """
    Stores the conversation history to provide context in future

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key conversation history that contains conversation
    """
    print("---GENERATE---")
    question = state["question"]
    generation=state["generation"]
    conversation_history= state.get("conversation_history",[])

    conversation_history.append({"question":question,"ai response":generation.content})
    return {"conversation_history":conversation_history}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    web_search = "No"
    for d in documents:
        doc_grader_prompt_formatted = doc_grader_prompt.format(
            document=d.page_content, question=question
        )
        result = llm2.invoke(
            [SystemMessage(content=doc_grader_instructions)]
            + [HumanMessage(content=doc_grader_prompt_formatted)]
        )
        # Check if 'yes' is present in the content (case-insensitive)
        grade = "yes" if "yes" in result.content.lower() else "no"
        # Document relevant
        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        # Document not relevant
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            # We do not include the document in filtered_docs
            # We set a flag to indicate that we want to run web search
            web_search = "Yes"
            continue
    return {"documents": filtered_docs, "web_search": web_search}


def web_search(state):
    """
    Web search based based on the question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Appended web results to documents
    """

    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    documents.append(web_results)
    return {"documents": documents}


### Edges


def route_question(state):
    """
    Route question to web search or RAG

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    route_question = llm.invoke(
        [SystemMessage(content=router_instructions)]
        + [HumanMessage(content=state["question"])]
    )
    source = (
        "vectorstore" if "vectorstore" in route_question.content.lower() 
        else "websearch" if "websearch" in route_question.content.lower() 
        else "chat_bot"
    )
    if source == "websearch":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "websearch"
    elif source == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
    else:
        print("---ROUTE QUESTION TO General LLM---")
        return "chat_bot"



def decide_to_generate(state):
    """
    Determines whether to generate an answer, or add web search

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    question = state["question"]
    web_search = state["web_search"]
    filtered_documents = state["documents"]

    if web_search == "Yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: NOT ALL DOCUMENTS ARE RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return "websearch"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state.get("documents",[])
    generation = state["generation"]
    max_retries = state.get("max_retries", 3)  # Default to 3 if not provided

    hallucination_grader_prompt_formatted = hallucination_grader_prompt.format(
        documents=format_docs(documents), generation=generation.content
    )
    result = llm3.invoke(
        [SystemMessage(content=hallucination_grader_instructions)]
        + [HumanMessage(content=hallucination_grader_prompt_formatted)]
    )
    grade = "yes" if "yes" in result.content.lower() else "no"
    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        # Test using question and generation from above
        answer_grader_prompt_formatted = answer_grader_prompt.format(
            question=question, generation=generation.content
        )
        result = llm2.invoke(
            [SystemMessage(content=answer_grader_instructions)]
            + [HumanMessage(content=answer_grader_prompt_formatted)]
        )
        grade = "yes" if "yes" in result.content.lower() else "no"
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        elif state["loop_step"] <= max_retries:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
        else:
            print("---DECISION: MAX RETRIES REACHED---")
            return "max retries"
    elif state["loop_step"] <= max_retries:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"
    else:
        print("---DECISION: MAX RETRIES REACHED---")
        return "max retries"
    



workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("websearch", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate
workflow.add_node("chat_bot", chat_bot)  # chatbot
workflow.add_node("store_history", store_history)  # stores conversation history

# Build graph
workflow.set_conditional_entry_point(
    route_question,
    {
        "websearch": "websearch",
        "vectorstore": "retrieve",
        "chat_bot": "chat_bot",
    },
)
workflow.add_edge("chat_bot", "store_history")
workflow.add_edge("websearch", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "websearch": "websearch",
        "generate": "generate",
    },
)
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": "store_history",
        "not useful": "websearch",
        "max retries": "store_history",
    },
)
workflow.add_edge("store_history",END)

memory = MemorySaver()
# Compile
graph = workflow.compile(checkpointer=memory)
png_data = graph.get_graph().draw_mermaid_png()

# Save it to a file
with open("graph_output.png", "wb") as f:
    f.write(png_data)
