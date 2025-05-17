# import os
# import pandas as pd

# def load_corpora(path, sender_id: int):
#     df = pd.read_csv(path)[['Sender ID', 'Message']]
#     df["Is Me"] = (df["Sender ID"] == sender_id).astype(int)
#     full_history = df["Message"].astype(str).str.strip().tolist()
#     my_corpus    = (
#         df.loc[df["Is Me"] == 1, "Message"].astype(str).str.strip().tolist()
#     )
#     return full_history, my_corpus


# CHAT_CSV = os.getenv("CHAT_HISTORY_PATH", "data/big_chat.csv")
# SENDER_ID = int(os.getenv("MY_SENDER_ID", 379999478))

# a, b = load_corpora(CHAT_CSV, SENDER_ID)
# print(a)