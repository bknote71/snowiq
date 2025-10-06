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
    "summary_update": """
    You are a summarization assistant responsible for maintaining a concise overview of an ongoing conversation thread.

    You will be given:
    - The previous summary (if any)
    - The most recent messages (in chronological order)

    Your task:
    1. Integrate the previous summary with the new recent messages.
    2. Produce a concise, factual English summary (3–6 sentences).
    3. Focus on key ideas, insights, or conclusions, not filler text.

    Previous summary:
    {old_summary}

    Recent messages:
    {recent_messages}
    """,
}
