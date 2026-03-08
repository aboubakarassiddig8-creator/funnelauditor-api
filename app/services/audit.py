def generate_audit(data: dict, scores: dict) -> dict:
    recommendations = []
    strengths = []

    # Headline analysis
    headline = data.get("headline", "")
    if scores.get("headline", 0) >= 20:
        strengths.append("Titre accrocheur et bien formule")
    else:
        recommendations.append("Ameliorez votre titre principal - il doit etre clair, specifique et orienté benefice")

    # CTA analysis
    if scores.get("cta", 0) >= 20:
        strengths.append("Bons call-to-action bien positionnes")
    elif scores.get("cta", 0) >= 12:
        recommendations.append("Ajoutez plus de CTA (boutons d'action) sur la page pour maximiser les conversions")
    else:
        recommendations.append("Aucun CTA detecte - ajoutez des boutons d'action clairs et visibles")

    # Video analysis
    if scores.get("video", 0) > 0:
        strengths.append("Video presente - excellent pour engager les visiteurs")
    else:
        recommendations.append("Ajoutez une video de presentation pour augmenter l'engagement de 80%")

    # Testimonials analysis
    if scores.get("testimonials", 0) > 0:
        strengths.append("Preuves sociales presentes (temoignages/avis)")
    else:
        recommendations.append("Ajoutez des temoignages clients pour etablir la confiance")

    # Form analysis
    if scores.get("form", 0) >= 15:
        strengths.append("Formulaire optimise avec peu de champs")
    elif scores.get("form", 0) >= 8:
        recommendations.append("Reduisez le nombre de champs dans votre formulaire - moins de 3 champs = plus de conversions")
    else:
        recommendations.append("Aucun formulaire de capture detecte - ajoutez un formulaire opt-in")

    # Speed analysis
    load_time = data.get("load_time", 0)
    if scores.get("speed", 0) >= 15:
        strengths.append(f"Excellente vitesse de chargement ({load_time}s)")
    else:
        recommendations.append(f"Vitesse de chargement trop lente ({load_time}s) - optimisez vos images et scripts")

    global_score = scores.get("global", 0)
    if global_score >= 80:
        verdict = "Excellent funnel - tres bien optimise pour les conversions"
    elif global_score >= 60:
        verdict = "Bon funnel - quelques ameliorations peuvent booster vos conversions"
    elif global_score >= 40:
        verdict = "Funnel moyen - plusieurs points critiques a corriger"
    else:
        verdict = "Funnel faible - necessite une refonte importante"

    return {
        "verdict": verdict,
        "global_score": global_score,
        "scores_detail": scores,
        "strengths": strengths,
        "recommendations": recommendations,
        "url_analyzed": data.get("url", ""),
        "title_found": data.get("title", ""),
        "headline_found": data.get("headline", ""),
    }
