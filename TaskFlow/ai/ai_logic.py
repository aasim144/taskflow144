from datetime import date

def suggest_priority(deadline):
    days_left = (deadline - date.today()).days

    if days_left <= 2:
        return "High"
    elif days_left <= 5:
        return "Medium"
    else:
        return "Low"
