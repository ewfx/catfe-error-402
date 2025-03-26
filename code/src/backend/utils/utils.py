from models.llama import summarize_text
import time

# def chunk_to_text(chunk):
#     texts = [chunk["heading"]]
#     for c in chunk["content"]:
#         texts.append(f"{c['type'].capitalize()}: {c['data']}")
#     return "\n".join(texts)

def chunk_to_text(chunk):
    texts = [chunk["heading"]]
    for c in chunk["content"]:
        texts.append(f"{c['type'].capitalize()}: {get_text(c)}")
    return "\n".join(texts)

def get_text(content):
    if(isinstance(content["data"], str)):
        return content["data"]
    texts = []
    if content.get("heading"):
        texts.append(content.get("heading"))
        for d in content["data"]:
            texts.append(f"{get_text(d)}")
    # if content.get("data"):
    #     data = content.get("data")
    #     if isinstance(data, str):
    #         texts.append(data)
    #     else:
    #         for d in data:
    #             if isinstance(d, str):
    #                 texts.append(d)
    #             else:
    #                 texts.append(get_text(d))
                
    return "\n".join(texts)


def chunk_to_text_llama(chunk):
    prompt = f"Summarize the below provided chunk in such a way that it can be used directly for vector embedding by the sentence-transformers/all-mpnet-base-v2 model without missing any detail. Also make sure there is nothing else in the response other than the summary. '''{chunk}''' The chunk is structured in json format in such a way that heading represents what is present in the content or the data key. type represents how important this block really is?"
    system_message = """You are a highly efficient assistant designed to generate detailed and accurate summaries of the text taken from the documentation of a project. Your primary goal is to summarize the provided text retaining all the information. You should only provide the summary in the response and nothing else."""
    summary = summarize_text(prompt=prompt, system_message=system_message)
    print(summary)
    time.sleep(20)
    return summary