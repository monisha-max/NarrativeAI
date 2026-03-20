GUIDED_PROMPTS = {
    "explain": {
        "label": "Explain the story",
        "prompt": "Provide a full narrative synthesis of this dossier at the user's maturity level. Start from the beginning, build context progressively, and end with the current state.",
    },
    "what_changed": {
        "label": "What changed today?",
        "prompt": "Show only what changed since the user's last visit. Rank by significance, not recency. Include: new events, sentiment shifts, predictions confirmed/invalidated, phase changes.",
    },
    "who_exposed": {
        "label": "Who is exposed?",
        "prompt": "Generate a consequence map: all stakeholders affected by the latest developments. Include sector impact chains (first and second order). Name specific entities.",
    },
    "opposing_takes": {
        "label": "Give me opposing takes",
        "prompt": "Present the consensus view and the strongest contrarian view side by side. Include evidence comparison and unresolved questions.",
    },
    "timeline": {
        "label": "Show me timeline",
        "prompt": "Return the interactive timeline data with events, fog overlay, and sentiment markers.",
    },
    "eli19": {
        "label": "Explain like I'm 19",
        "prompt": "Retell the entire story with zero jargon, relatable analogies, and foundational explanations. Every financial term gets an inline definition. Contextualize all numbers.",
    },
    "what_if_wrong": {
        "label": "What if I'm wrong?",
        "prompt": "Infer the user's current position and build the strongest possible case against it. Use evidence from the dossier corpus.",
    },
    "portfolio_relevant": {
        "label": "Relevant to my portfolio",
        "prompt": "Analyze how this story impacts the user's sectors of interest. Include specific stock/sector implications, risk assessment, and actionable insights.",
    },
    "story_dna": {
        "label": "What's the story's DNA?",
        "prompt": "Identify the story's archetype, current phase, historical parallels, and phase prediction. Show what typically happens next with confidence levels.",
    },
    "sixty_second": {
        "label": "60-second version",
        "prompt": "Three things only: (1) Most important change since last visit, (2) Biggest risk right now, (3) Most actionable insight. Be ruthlessly concise.",
    },
}
