def score_funnel(data: dict) -> dict:
    scores = {}

    # Score headline (0-20)
    headline = data.get("headline", "")
    if len(headline) > 30:
        scores["headline"] = 20
    elif len(headline) > 10:
        scores["headline"] = 12
    else:
        scores["headline"] = 5

    # Score CTA (0-20)
    cta_count = data.get("cta_count", 0)
    if cta_count >= 3:
        scores["cta"] = 20
    elif cta_count >= 1:
        scores["cta"] = 12
    else:
        scores["cta"] = 0

    # Score video (0-15)
    scores["video"] = 15 if data.get("has_video") else 0

    # Score testimonials (0-15)
    scores["testimonials"] = 15 if data.get("has_testimonials") else 0

    # Score form (0-15)
    form_fields = data.get("form_fields", 0)
    if data.get("has_form") and form_fields <= 3:
        scores["form"] = 15
    elif data.get("has_form"):
        scores["form"] = 8
    else:
        scores["form"] = 0

    # Score load time (0-15)
    load_time = data.get("load_time", 10)
    if load_time < 2:
        scores["speed"] = 15
    elif load_time < 4:
        scores["speed"] = 10
    else:
        scores["speed"] = 3

    total = sum(scores.values())
    scores["global"] = min(total, 100)

    return scores
