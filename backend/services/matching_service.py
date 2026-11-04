# This file calculates the matching percentage.

# We use weighted scoring:
# - Technical skills: 40%
# - Relevant experience: 30%
# - Project experience: 20%
# - Education and certifications: 10%
WEIGHTS = {

    "technical_skills": 0.40,

    "relevant_experience": 0.30,

    "project_experience": 0.20,

    "education_certifications": 0.10

}


def calculate_match_percentage(
    category_scores: dict
) -> float:

    total_score = 0

    for category, weight in WEIGHTS.items():

        score = float(
            category_scores.get(category, 0)
        )

        score = max(
            0,
            min(100, score)
        )

        total_score += score * weight

    return round(total_score, 1)
