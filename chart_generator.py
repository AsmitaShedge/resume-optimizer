import matplotlib.pyplot as plt


def generate_chart(
    resume_score,
    ats_score,
    match_score
):

    labels = [
        "Resume Score",
        "ATS Score",
        "Match Score"
    ]

    scores = [
        resume_score,
        ats_score,
        match_score
    ]

    plt.figure(figsize=(6,4))

    plt.bar(labels, scores)

    plt.ylim(0,100)

    plt.title(
        "Resume Analysis"
    )

    plt.savefig(
        "reports/analysis_chart.png"
    )

    plt.close()