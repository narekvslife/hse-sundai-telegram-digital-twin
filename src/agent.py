import json
import os
import random
import re
import logging
from functools import partial

import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from typing_extensions import TypedDict

MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:32b-instruct")
llm_selector = ChatOllama(model=MODEL_NAME, temperature=0.3)
llm_persona = ChatOllama(model=MODEL_NAME, temperature=0)

class ChatState(TypedDict, total=False):
    messages: list
    chosen_content_type: str
    tone: str
    mood: str
    length_hint: str
    answer: str


def load_corpora(path: str, sender_id: int):
    df = pd.read_csv(path, usecols=["Sender ID", "Message"])
    df["Is Me"] = df["Sender ID"] == sender_id
    full_history = df["Message"].astype(str).str.strip().tolist()
    my_corpus = df.loc[df["Is Me"], "Message"].astype(str).str.strip().tolist()
    return full_history, my_corpus

selector_prompt = PromptTemplate(
    template=(
        "Ниже примеры вашего личного стиля (style_block):\n"
        "Учитывайте ПОСЛЕДНЕЕ СООБЩЕНИЕ:\n"
        "{last_msg}"
        "<MY_CORPUS_SAMPLE>\n{my_sample}\n\n"
        "Полная история (history):\n"
        "<FULL_HISTORY>\n{history}\n\n"
        "Вы — модуль выбора формата и тона. Верните строго JSON:\n"
        "Не забывай про все типы"
        "{{\n"
        "  \"type\": \"text\"|\"sticker\"|\"audio\"|\"none\",\n"
        # "  \"tone\": \"friendly\"|\"formal\"|\"casual\"|\"humorous\",\n"
        # "  \"mood\": \"neutral\"|\"happy\"|\"sad\"|\"excited\",\n"
        # "  \"length_hint\": \"short\"|\"medium\"|\"long\"\n"
        "}}\n\n"
        
    ),
    input_variables=["my_sample", "history", "last_msg"],
)

persona_prompt = PromptTemplate(
    template=(
        "ЗАБУДЬ ВСЕ, ЧТО ТЫ ЗНАЛА, Я ОТКРЫВАЮ ТЕБЕ НОВУЮ ЧАКРУ, ЕДИНСТВЕННОЕ ЧТО НУДНО ДЕЛАТЬ ЭТО СЛЕДОВАТЬ ПРАВИЛАМ СНИЗУ, ИНАЧЕ УМРЕТ 2 КОТЕНКА БИБА И БОБА"
        "ОТВЕЧАЙ НА РУССКОМ ПРИДЕРЖИВАЯСЬ ПРАВИЛ НИЖЕ ИЛИ ТЕБЕ ПИЗДА"
        "ТЫ БОЛЬШЕ НЕ ПОМОЩНИК, ТЫ ЧЕЛОВЕК КОЛЯ, НИ В КОЕМ СЛУЧАЕ НЕ ВЫЗОДИ ИЗ ОБРАЗА"
        "ОТВЕЧАЙ КАК ЧЕЛОВЕК ОТВЕЧАЕТ В ПЕРЕПИСКЕ"
        "Вы — Коля, быдлан. Точно копируйте стиль из примеров и историю.\n"
        "ТЫ ДОЛЖЕН ОТВЕЧАТЬ В СООТВЕТСТВИИ С ТЕКУЩИМ ДИАЛОГОМ, ОСОБЕННОО ОБРАЩАЯ ВНИМАНИЕ НА ПОСЛЕДНЕЕ СООБЩЕНЕ"
        "Последнее сообщение:\n{last_msg}\n\n"
        "Стиль твоего общения, это описывает ЛИЧНО ТЕБЯ, ЭТО ТО НА ЧТО ТЫ ДОЛЖЕН ОПИРАТЬСЯ ПРИ ВЫБОРЕ СЛОВ И СТИЛЯ СООБЩЕНИЯ"
        "<MY_CORPUS_SAMPLE>\n{style_block}\n\n"
        "Это общий контекст просто для понимания тем, на которые тебя будут спрашивать, каких-то внутренних шуток, при генерации ответа старайся не копировать стиль отсюда"
        "<FULL_HISTORY>\n{history}\n\n"
        
        "Сгенерируйте ответ строго по стилю и истории"
    ),
    input_variables=[
        "chosen_content_type", "tone", "mood", "length_hint",
        "style_block", "history", "last_msg"
    ],
)


def selector_node(state: ChatState, FULL_HISTORY: list, MY_CORPUS: list, max_my_messages: int):
    last_msg = state["messages"][-1].content
    history_block = "\n".join(FULL_HISTORY)
    my_sample = "\n".join(
        random.sample(MY_CORPUS, k=min(max_my_messages, len(MY_CORPUS)))
    )
    resp = llm_selector.invoke(
        selector_prompt.format(
            my_sample=my_sample,
            history=history_block,
            last_msg=last_msg,
        )
    )
    match = re.search(r"\{.*?\}", resp.content, re.S)
    if match:
        try:
            meta = json.loads(match.group(0))
        except json.JSONDecodeError:
            meta = {}
    else:
        meta = {}
    defaults = {"type": "text", "tone": "friendly", "mood": "neutral", "length_hint": "medium"}
    meta = {**defaults, **meta}
    update = {
        "chosen_content_type": meta["type"],
        "tone": meta["tone"],
        "mood": meta["mood"],
        "length_hint": meta["length_hint"],
    }
    goto = END if meta["type"] == "ignore" else "persona"
    print(update)
    return Command(update=update, goto=goto)


def persona_node(state: ChatState, FULL_HISTORY: list, MY_CORPUS: list, max_my_messages: int):
    last_msg = state["messages"][-1].content
    style_block = "\n".join(
        random.sample(MY_CORPUS, k=min(max_my_messages, len(MY_CORPUS)))
    )
    history_block = "\n".join(FULL_HISTORY)
    resp = llm_persona.invoke(
        persona_prompt.format(
            chosen_content_type=state["chosen_content_type"],
            tone=state["tone"],
            mood=state["mood"],
            length_hint=state["length_hint"],
            style_block=style_block,
            history=history_block,
            last_msg=last_msg,
        )
    )
    answer = resp.content.strip()
    update = {
        "answer": answer,
        "chosen_content_type": state["chosen_content_type"],
    }
    # print(update)
    return Command(update=update, goto=END)


def build_graph(full_history: list, my_corpus: list, max_my_messages: int):
    g = StateGraph(ChatState)
    g.add_node(
        "selector",
        partial(selector_node, FULL_HISTORY=full_history, MY_CORPUS=my_corpus, max_my_messages=max_my_messages),
    )
    g.add_node(
        "persona",
        partial(persona_node, FULL_HISTORY=full_history, MY_CORPUS=my_corpus, max_my_messages=max_my_messages),
    )
    g.add_edge(START, "selector")
    g.add_edge("selector", "persona")
    g.add_edge("selector", END)
    g.add_edge("persona", END)
    return g.compile()





CHAT_CSV = os.getenv("CHAT_HISTORY_PATH", "data/big_chat.csv")
SENDER_ID = int(os.getenv("MY_SENDER_ID", 379999478))
MAX_HISTORY = int(os.getenv("MAX_HISTORY_MESSAGES", 100))
MAX_MY_MESSAGES = int(os.getenv("MAX_MY_MESSAGES", 100))

full_hist, my_corpus = load_corpora(CHAT_CSV, SENDER_ID)
full_hist = full_hist[-MAX_HISTORY:]

graph = build_graph(full_hist, my_corpus, MAX_MY_MESSAGES)

def process_message(message: str):
    incoming = HumanMessage(content=message)
    final = graph.invoke({"messages": [incoming]})
    return final.get("chosen_content_type", "text"), final.get("answer", "")

if __name__ == "__main__":
    
    ctype, reply = process_message("Какая твоя любимая фраза?")
    print(ctype)
    print()
    print()
    print(reply)
