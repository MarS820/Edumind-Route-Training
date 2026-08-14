from collections import Counter
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def weak_topics(events: pd.DataFrame) -> list[str]:
    if events.empty:
        return []
    quiz = events[(events["event_type"] == "quiz_submitted") & events["topic"].notna()].copy()
    if quiz.empty:
        return []
    quiz["rate"] = quiz["score"] / quiz["total"].replace(0, 1)
    
    if "timestamp" in quiz.columns:
        max_time = quiz["timestamp"].max()
        quiz["days_ago"] = (max_time - quiz["timestamp"]).dt.days
        quiz["weight"] = np.exp(-0.1 * quiz["days_ago"])
    else:
        quiz["weight"] = 1.0
    
    grouped = quiz.groupby("topic").apply(lambda x: np.average(x["rate"], weights=x["weight"]) if len(x) > 0 else x["rate"].mean()).sort_values(ascending=True)
    
    topic_counts = quiz["topic"].value_counts()
    weak_list = []

    for topic in grouped[grouped < 0.75].index[:6]:
        attempts = topic_counts.get(topic, 0)
        if grouped[topic] <0.6 and attempts >= 2:
            weak_list.insert(0, topic)
        else: 
            weak_list.append(topic)
    return weak_list

def strong_topics(events: pd.DataFrame) -> list[str]:
    if events.empty:
        return []
    
    quiz = events[(events["event_type"] == "quiz_submitted") & events["topic"].notna()].copy()
    if quiz.empty:
        return []
    
    quiz["rate"] = quiz["score"] / quiz["total"].replace(0, 1)
    
    topic_counts = quiz["topic"].value_counts()
    
    grouped = quiz.groupby("topic")["rate"].mean().sort_values(ascending=False)
    
    strong_list = []
    for topic in grouped[grouped >= 0.8].index[:6]:
        attempts = topic_counts.get(topic, 0)
        confidence_boost = min(attempts * 0.05, 0.15)
        adjusted_score = grouped[topic] + confidence_boost
        
        if adjusted_score >= 0.85:
            strong_list.insert(0, topic)
        else: 
            strong_list.append(topic)
    return strong_list[:4]

def get_learning_pace(events: pd.DataFrame) -> dict:
    if events.empty or "timestamp" not in events.columns:
        return {"pace": "steady", "consistency": "unknown"}
    
    events["date"] = events["timestamp"].dt.date
    daily_activity = events.groupby("date").size()
    
    if len(daily_activity) < 2:
        return {"pace": "starting", "consistency": "new_learner"}
    
    mean_activity = daily_activity.mean()
    std_activity = daily_activity.std()
    cv = std_activity / mean_activity if mean_activity > 0 else 1.0
    
    if cv < 0.3:
        consistency = "highly_consistent"
        pace = "steady"
    elif cv < 0.6:
        consistency = "moderately_consistent"
        pace = "irregular"
    else:
        consistency = "inconsistent"
        pace = "sporadic"
        
    recent_avg = daily_activity.tail(3).mean() if len(daily_activity) >= 3 else daily_activity.mean()
    overall_avg = daily_activity.mean()
    
    if recent_avg > overall_avg * 1.2:
        pace = "accelerating"
    elif recent_avg < overall_avg * 0.8:
        pace = "slowing"
    return {"pace": pace, "consistency": consistency}

def topic_engagement(events: pd.DataFrame) -> dict:
    """Analyze topic engagement patterns"""
    if events.empty:
        return {"most_engaged": [], "least_engaged": []}
    
    topic_activity = events[events["topic"].notna()].groupby("topic").size().sort_values(ascending=False)
    
    return {
        "most_engaged": topic_activity.head(3).index.tolist(),
        "least_engaged": topic_activity.tail(3).index.tolist(),
        "total_topics": len(topic_activity)
    }   

def recommendation_plan(events: pd.DataFrame) -> list[str]:
    weak = weak_topics(events)
    strong = strong_topics(events)
    recent_counts = Counter(events["event_type"]) if not events.empty else Counter()
    engagement = topic_engagement(events)
    learning_pace = get_learning_pace(events)
    
    plan = []
    
    if weak:
        # Prioritize the weakest topic first
        weakest = weak[0]
        plan.append(f"🔴 <b>Priority</b>: Start with 10 minutes of flashcards on <b>{weakest}</b>, then take a medium quiz.")
        
        if len(weak) > 1:
            plan.append(f"📋 <b>Secondary</b>: Review {weak[1]} and try 5 practice questions.")
        
        if len(weak) >= 3:
            plan.append(f"📚 <b>Study session</b>: Combine {weak[0]}, {weak[1]}, and {weak[2]} for a 20-minute review.")
    else:
        plan.append("✅ <b>No weak topics detected</b>. Take a diagnostic quiz to maintain your edge.")
    
    # 2. Strong topics - encourage teaching/practice
    if strong:
        plan.append(f"💪 <b>Leverage your strengths</b>: You excel at {strong[0]}. Consider explaining it to someone else (or ChatGPT) to deepen understanding.")
    
    # 3. PDF engagement
    if recent_counts["pdf_question"] < 3:
        plan.append("📄 <b>Knowledge gap</b>: Upload a lecture PDF and ask at least 3 questions about unclear sections.")
    elif recent_counts["pdf_question"] >= 5:
        plan.append("📄 <b>Great engagement!</b> You're actively learning from PDFs. Try generating practice questions from your next PDF.")
    
    # 4. Assignment generation
    if recent_counts["assignment_generated"] < 1:
        plan.append("✍️ <b>Active recall</b>: Generate one assignment from your lecture notes to turn passive reading into practice.")
    else:
        plan.append("📝 <b>Practice makes perfect</b>: Review your last assignment and try to improve your score.")
    
    # 5. Learning pace insights
    if learning_pace["pace"] == "accelerating":
        plan.append("🚀 <b>You're on a roll!</b> Increase difficulty to stay challenged.")
    elif learning_pace["pace"] == "slowing":
        plan.append("🔄 <b>Take a breather</b>: Review your notes before the next session.")
    elif learning_pace["consistency"] == "inconsistent":
        plan.append("📅 <b>Consistency tip</b>: Try 15 minutes daily instead of 2 hours weekly.")
    
    # 6. Engagement insights
    if engagement["most_engaged"]:
        plan.append(f"🎯 <b>You're most engaged with</b>: {', '.join(engagement['most_engaged'])}. Great focus!")
    
    if engagement["least_engaged"] and len(engagement["least_engaged"]) > 0:
        if engagement["least_engaged"][0] != engagement["most_engaged"][0] if engagement["most_engaged"] else True:
            plan.append(f"💡 <b>Balance your learning</b>: Spend some time on {', '.join(engagement['least_engaged'])}.")
    
    # 7. Review missed questions
    if recent_counts.get("quiz_submitted", 0) > 2:
        plan.append("📖 <b>Review explanations for every missed quiz question before increasing difficulty.</b>")
    
    # 8. Personal touch based on overall progress
    total_events = len(events)
    if total_events > 50:
        plan.append("🏆 <b>Great progress!</b> You're building strong learning habits. Keep it up!")
    elif total_events > 20:
        plan.append("🌟 <b>Good momentum</b> - you're on the right track!")
    
    return plan


def get_learning_insights(events: pd.DataFrame) -> dict:
    """Get comprehensive learning insights"""
    if events.empty:
        return {
            "weak_topics": [],
            "strong_topics": [],
            "recommendations": ["Start your learning journey by uploading some materials!"],
            "metrics": {}
        }
    
    return {
        "weak_topics": weak_topics(events),
        "strong_topics": strong_topics(events),
        "recommendations": recommendation_plan(events),
        "learning_pace": get_learning_pace(events),
        "topic_engagement": topic_engagement(events),
        "metrics": {
            "total_events": len(events),
            "quiz_count": len(events[events["event_type"] == "quiz_submitted"]),
            "pdf_questions": len(events[events["event_type"] == "pdf_question"]),
            "assignments": len(events[events["event_type"] == "assignment_generated"]),
            "unique_topics": len(events[events["topic"].notna()]["topic"].unique())
        }
    }
