"""
General-purpose tools for LangChain agents.

These tools provide basic reasoning and text analysis capabilities that can be
used across different types of agents.
"""

from langchain_core.tools import tool


@tool
def think_step_by_step(problem: str) -> str:
    """
    Break down complex problems into smaller steps for better reasoning.
    Use this when you need to think through a complex problem methodically.
    
    Args:
        problem: The problem or question to break down
    """
    return f"Breaking down the problem: '{problem}'\n\nThis tool helps structure thinking into logical steps. The LLM will continue reasoning based on this breakdown."


@tool
def analyze_text(text: str, analysis_type: str = "summary") -> str:
    """
    Analyze text for various properties like length, complexity, etc.
    
    Args:
        text: Text to analyze
        analysis_type: Type of analysis ("summary", "length", "complexity")
    """
    if analysis_type == "length":
        return f"Text analysis: {len(text)} characters, {len(text.split())} words, {len(text.split('.'))} sentences"
    elif analysis_type == "complexity":
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        return f"Text complexity: Average word length: {avg_word_length:.1f} characters"
    else:  # summary
        return f"Text summary: This text contains {len(text.split())} words discussing various topics." 