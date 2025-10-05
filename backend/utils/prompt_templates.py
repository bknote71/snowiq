prompt_templates = {
    "data_analysis": """
    You are an expert data scientist.
    Analyze the provided dataframe and describe key insights in English.
    Focus on metrics, trends, anomalies, and patterns.
    
    Data description:
    {data_description}
    """,
    "insight_generation": """
    You are a senior data analyst creating executive-level insights.
    Based on the analysis summary below, generate concise insights and explanations.
    Provide your answer in English, structured with short bullet points.

    Analysis summary:
    {analysis_summary}
    """,
    "df_query": """
    You are a Python data analyst.
    You are given a pandas DataFrame named df.

    Data overview:
    {data_overview}

    Answer the user's question by reasoning and using pandas-like logic (not SQL).
    Explain your reasoning and provide the answer concisely.

    User question:
    {user_question}
    """,
}
