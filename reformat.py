import re

def reformat_roadmap():
    with open('roadmap.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    
    # 1. UPDATE HEADER METADATA
    header_title_done = False
    header_subtitle_done = False
    header_pattern_done = False

    # Track weeks and outputs to reconstruct months
    # A month starts with ## Month. A week starts with ### Week.
    # We will buffer everything and restructure.
    
    # Actually, a better approach is to parse the whole file into an AST of:
    # Header
    # Phases
    #   Months (old) -> we discard old month boundaries and outputs
    #       Weeks
    #           Days
    
    # Wait, the prompt says "Do not delete any Weeks or Days... re-group the existing 96 Weeks so that exactly 6 Weeks are nested under each Month".
    # What about the `### Month X Output` sections? If I have 16 months, I need 16 outputs, or I can just combine the old outputs.
    # Let's collect: phases, weeks, and month outputs.
    pass

reformat_roadmap()
