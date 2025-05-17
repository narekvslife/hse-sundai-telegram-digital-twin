import json
import os
import random
import re
from functools import partial
from pathlib import Path

import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command


MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:0.6b")
llm_selector = ChatOllama(model=MODEL_NAME, temperature=0.3)
llm_persona  = ChatOllama(model=MODEL_NAME, temperature=0.7)


def load_corpora(path: str | Path, sender_id: int):
    df = pd.read_csv(path)
    df["Is Me"] = (df["Sender ID"] == sender_id).astype(int)
    full_history = df["Content"].astype(str).str.strip().tolist()
    my_corpus    = (
        df.loc[df["Is Me"] == 1, "Content"].astype(str).str.strip().tolist()
    )
    return full_history, my_corpus


selector_prompt = PromptTemplate(
    template=(
        "Ты — модуль выбора формата и стиля ответа.\n"
        "Верни ЧИСТЫЙ JSON вида:\n"
        "{{\n"
        '  "type":        "text|sticker|audio|ignore",\n'
        '  "tone":        "formal|friendly|ironic|playful",\n'
        '  "mood":        "neutral|enthusiastic|sympathetic|humorous",\n'
        '  "length_hint": "short|medium|detailed"\n'
        "}}\n\n"
        "Кратко определи стиль, исходя из последнего сообщения и контекста.\n\n"
        "Последнее сообщение пользователя:\n{last_msg}\n\n"
        "<FULL_HISTORY>\n{history}\n\n"
        "<MY_CORPUS_SAMPLE>\n{my_sample}"
    ),
    input_variables=["last_msg", "history", "my_sample"],
) 

def selector_node(state, FULL_HISTORY, MY_CORPUS, max_my_messages):
    last_msg = state["messages"][-1].content
    history_block = "\n".join(FULL_HISTORY)
    sample_size   = min(max_my_messages, len(MY_CORPUS))
    my_sample     = "\n".join(random.sample(MY_CORPUS, k=sample_size))

    resp = llm_selector.invoke(
        selector_prompt.format(
            last_msg=last_msg,
            history=history_block,
            my_sample=my_sample,
        )
    )

    defaults = {"type": "text", "tone": "friendly",
                "mood": "neutral", "length_hint": "medium"}

    try:
        meta = json.loads(re.search(r"{.*}", resp.content, re.S).group(0))
    except Exception:
        meta = {}
    meta = {**defaults, **meta}

    update = {
        "chosen_content_type": meta["type"],
        "tone":        meta["tone"],
        "mood":        meta["mood"],
        "length_hint": meta["length_hint"],
    }
    goto = END if meta["type"] == "ignore" else "persona"
    return Command(update=update, goto=goto)


PERSONA_SYSTEM = (
    "Ты — <Имя>. Пиши в тоне {tone}, настроение {mood}, объём {length_hint}."
)

def persona_node(state, FULL_HISTORY, MY_CORPUS, max_my_messages):
    cfg       = dict(state)
    last_msg  = cfg["messages"][-1].content

    sample_size  = min(max_my_messages, len(MY_CORPUS))
    style_block  = "\n".join(random.sample(MY_CORPUS, k=sample_size))
    history_block = "\n".join(FULL_HISTORY)

    prompt = (
        PERSONA_SYSTEM.format(
            tone=cfg.get("tone", "friendly"),
            mood=cfg.get("mood", "neutral"),
            length_hint=cfg.get("length_hint", "medium"),
        )
        + f"\n\n<MY_CORPUS>\n{style_block}"
        + f"\n\n<FULL_HISTORY>\n{history_block}"
        + f"\n\n<USER_MSG>\n{last_msg}\n\n"
        "Ответь подходящим образом."
    )

    answer = llm_persona.invoke(prompt).content.strip()
    return Command(update={"response": answer}, goto=END)

def build_graph(FULL_HISTORY, MY_CORPUS, max_my_messages):
    g = StateGraph(MessagesState)

    g.add_node(
        "selector",
        partial(
            selector_node,
            FULL_HISTORY=FULL_HISTORY,
            MY_CORPUS=MY_CORPUS,
            max_my_messages=max_my_messages,
        ),
    )
    g.add_node(
        "persona",
        partial(
            persona_node,
            FULL_HISTORY=FULL_HISTORY,
            MY_CORPUS=MY_CORPUS,
            max_my_messages=max_my_messages,
        ),
    )

    g.add_edge(START, "selector")
    g.add_edge("selector", "persona")
    g.add_edge("selector", END)
    g.add_edge("persona", END)

    return g.compile()


def process_message(message: str):
    graph = build_graph(full_hist, my_corpus, MAX_MY_MESSAGES)
    incoming = HumanMessage(content=message)
    final    = graph.invoke({"messages": [incoming]})
    print(final)
    return (
        final.get("chosen_content_type", "text"),
        final.get("response", ""),
    )


if __name__ == "__main__":
    CHAT_CSV          = os.getenv("CHAT_HISTORY_PATH", "src/data/chat_export.csv")
    SENDER_ID         = int(os.getenv("MY_SENDER_ID", 379999478))
    MAX_HISTORY       = int(os.getenv("MAX_HISTORY_MESSAGES", 10))
    MAX_MY_MESSAGES   = int(os.getenv("MAX_MY_MESSAGES", 10))

    full_hist, my_corpus = load_corpora(CHAT_CSV, SENDER_ID)
    full_hist = full_hist[-MAX_HISTORY:]

    graph = build_graph(full_hist, my_corpus, MAX_MY_MESSAGES)

    test_text = "Привет, обязательно ответь на это сообщение"
    ctype, reply = process_message(graph, test_text)
    print(f"[{ctype}] → {reply}")
