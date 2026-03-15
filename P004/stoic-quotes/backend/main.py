from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

QUOTES = [
    {"text": "You have power over your mind, not outside events. Realize this, and you will find strength.", "author": "Marcus Aurelius"},
    {"text": "The impediment to action advances action. What stands in the way becomes the way.", "author": "Marcus Aurelius"},
    {"text": "Waste no more time arguing about what a good man should be. Be one.", "author": "Marcus Aurelius"},
    {"text": "He who fears death will never do anything worthy of a living man.", "author": "Seneca"},
    {"text": "It is not that I'm so smart. But I stay with the questions much longer.", "author": "Epictetus"},
    {"text": "Make the best use of what is in your power, and take the rest as it happens.", "author": "Epictetus"},
    {"text": "No man is free who is not master of himself.", "author": "Epictetus"},
    {"text": "Luck is what happens when preparation meets opportunity.", "author": "Seneca"},
    {"text": "We suffer more in imagination than in reality.", "author": "Seneca"},
    {"text": "Begin at once to live, and count each separate day as a separate life.", "author": "Seneca"},
    {"text": "The first rule is to keep an untroubled spirit. The second is to look things in the face and know them for what they are.", "author": "Marcus Aurelius"},
    {"text": "If it is not right, do not do it; if it is not true, do not say it.", "author": "Marcus Aurelius"},
    {"text": "Confine yourself to the present.", "author": "Marcus Aurelius"},
    {"text": "How long are you going to wait before you demand the best for yourself?", "author": "Epictetus"},
    {"text": "Man is not worried by real problems so much as by his imagined anxieties about real problems.", "author": "Epictetus"},
    {"text": "Associate with people who are likely to improve you.", "author": "Seneca"},
    {"text": "Difficulties strengthen the mind, as labor does the body.", "author": "Seneca"},
    {"text": "He suffers more than necessary, who suffers before it is necessary.", "author": "Seneca"},
    {"text": "The whole future lies in uncertainty: live immediately.", "author": "Seneca"},
    {"text": "Receive without pride, relinquish without struggle.", "author": "Marcus Aurelius"},
]

@app.get("/quote")
def get_quote():
    return random.choice(QUOTES)
