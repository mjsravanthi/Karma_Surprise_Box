
# # app/main.py

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Dict
# from app.model_utils import predict_surprise
# from app.reward_engine import determine_box_type, generate_reason, determine_rarity, generate_status

# app = FastAPI()

# # Optional: Allow CORS for frontend access (you can restrict the origins in prod)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change to your frontend domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Input Models
# class DailyMetrics(BaseModel):
#     login_streak: int
#     posts_created: int
#     comments_written: int
#     upvotes_received: int
#     quizzes_completed: int
#     buddies_messaged: int
#     karma_spent: int
#     karma_earned: int
#     spam: bool

# class SurpriseRequest(BaseModel):
#     user_id: str
#     date: str
#     daily_metrics: DailyMetrics

# # Main Surprise Box Check Endpoint
# @app.post("/check-surprise-box")
# def check_surprise_box(req: SurpriseRequest) -> Dict:
#     f = req.daily_metrics.dict()

#     # Basic data validation
#     if f["karma_earned"] < 0 or f["karma_spent"] < 0:
#         return {
#             "error": "karma_earned and karma_spent must be non-negative integers"
#         }

#     surprise_unlocked = predict_surprise(f)

#     if surprise_unlocked:
#         box_type = determine_box_type(f)
#         karma = abs(f["karma_earned"] - f["karma_spent"])
#         reason = generate_reason(karma, f, box_type)
#         rarity = determine_rarity(karma, box_type, f)
#     else:
#         box_type = ""
#         reason = "spam" if f["spam"] else "low_karma_diff"
#         karma = 0
#         rarity = ""

#     return {
#         "user_id": req.user_id,
#         "surprise_unlocked": surprise_unlocked,
#         "reward_karma": karma,
#         "reason": reason,
#         "rarity": rarity,
#         "box_type": box_type,
#         "status": generate_status(surprise_unlocked)
#     }

# # Health Check Endpoint
# @app.get("/health")
# def health() -> Dict:
#     return {"status": "ok"}

# # Version Endpoint with Safe File Reading
# @app.get("/version")
# def version() -> Dict:
#     try:
#         with open("app/version.txt") as f:
#             return {"version": f.read().strip()}
#     except FileNotFoundError:
#         return {"error": "version.txt not found"}
#     except Exception as e:
#         return {"error": str(e)}

# # Root Endpoint
# @app.get("/")
# def root() -> Dict:
#     return {
#         "message": "Karma Box is running. Visit /docs for the API documentation."
#     }









# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from app.model_utils import predict_surprise
from app.reward_engine import (
    determine_box_type,
    generate_reason,
    determine_rarity,
    generate_status,
    set_random_seed  # ✅ Added for deterministic random seed
)

app = FastAPI()

# Optional: Allow CORS for frontend access (you can restrict the origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Models
class DailyMetrics(BaseModel):
    login_streak: int
    posts_created: int
    comments_written: int
    upvotes_received: int
    quizzes_completed: int
    buddies_messaged: int
    karma_spent: int
    karma_earned: int
    spam: bool

class SurpriseRequest(BaseModel):
    user_id: str
    date: str
    daily_metrics: DailyMetrics

# Main Surprise Box Check Endpoint
@app.post("/check-surprise-box")
def check_surprise_box(req: SurpriseRequest) -> Dict:
    f = req.daily_metrics.dict()

    # Basic data validation
    if f["karma_earned"] < 0 or f["karma_spent"] < 0:
        return {
            "error": "karma_earned and karma_spent must be non-negative integers"
        }

    # ✅ Set deterministic seed using user_id and date
    set_random_seed(req.user_id, req.date)

    surprise_unlocked = predict_surprise(f)

    if surprise_unlocked:
        box_type = determine_box_type(f)
        karma = abs(f["karma_earned"] - f["karma_spent"])
        reason = generate_reason(karma, f, box_type)
        rarity = determine_rarity(karma, box_type, f)
    else:
        box_type = ""
        reason = "spam" if f["spam"] else "low_karma_diff"
        karma = 0
        rarity = ""

    return {
        "user_id": req.user_id,
        "surprise_unlocked": surprise_unlocked,
        "reward_karma": karma,
        "reason": reason,
        "rarity": rarity,
        "box_type": box_type,
        "status": generate_status(surprise_unlocked)
    }

# Health Check Endpoint
@app.get("/health")
def health() -> Dict:
    return {"status": "ok"}

# Version Endpoint with Safe File Reading
@app.get("/version")
def version() -> Dict:
    try:
        with open("app/version.txt") as f:
            return {"version": f.read().strip()}
    except FileNotFoundError:
        return {"error": "version.txt not found"}
    except Exception as e:
        return {"error": str(e)}

# Root Endpoint
@app.get("/")
def root() -> Dict:
    return {
        "message": "Karma Box is running. Visit /docs for the API documentation."
    }
