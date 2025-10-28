"""
Multi-Agent System for NF-e Processing

This package implements a CrewAI-based multi-agent system for processing
electronic invoices (NF-e) and answering user queries.

Main Components:
- NFeCrew: Main crew orchestrating the multi-agent system
- Tools: Database and schema query tools
- Config: Agent and task configurations in YAML

Usage:
    from agents import NFeCrew
    
    crew = NFeCrew()
    response = crew.process_message("Quantas notas fiscais foram emitidas hoje?")
"""

from agents.crew import NFeCrew, create_nfe_crew

__all__ = [
    "NFeCrew",
    "create_nfe_crew"
]

