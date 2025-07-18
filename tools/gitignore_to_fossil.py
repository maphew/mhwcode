#!/usr/bin/env python3
"""
Convert .gitignore patterns to Fossil's ignore format with a side-by-side comparison.

Usage:
    python gitignore_to_fossil.py [.gitignore_file]
    
If no file is provided, looks for .gitignore in the current directory.
"""

# todo: 
#   - add: show existing fossil ignore patterns
#   - add: show 3-way diff & merge of git and fossil ignore patterns
#   - add: write to .fossil-settings/ignore-glob
#   - add: write to alternate filename
# 

import os
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class PatternPair:
    original: str
    converted: List[str]

def convert_gitignore_to_fossil(gitignore_content: str) -> List[PatternPair]:
    """
    Convert gitignore patterns to Fossil ignore patterns.
    
    Args:
        gitignore_content: Content of .gitignore file as a string
        
    Returns:
        List[PatternPair]: List of original and converted patterns
    """
    patterns = []
    
    for line in gitignore_content.splitlines():
        # Skip empty lines and comments
        original = line.rstrip()
        if not original or original.startswith('#'):
            patterns.append(PatternPair(original, [original]))
            continue
            
        converted = []
        pattern = original.strip()
        
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            dir_pattern = pattern.rstrip('/')
            converted.append(f"{dir_pattern}/*")
            converted.append(f"{dir_pattern}/")
        # Handle patterns with wildcards
        elif '*' in pattern or '?' in pattern or '[' in pattern:
            converted.append(pattern)
        # Simple file/directory patterns
        else:
            if '/' in pattern:
                # Path with directories
                converted.append(pattern)
            else:
                # Simple filename
                converted.append(f"**/{pattern}")
                converted.append(f"**/{pattern}/*")
        
        patterns.append(PatternPair(original, converted or [pattern]))
    
    return patterns

def print_rich_comparison(patterns: List[PatternPair]) -> None:
    """Display the comparison using rich for better formatting."""
    console = Console()
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column(".gitignore", style="cyan", no_wrap=True)
    table.add_column("Fossil Ignore", style="green")
    
    for pair in patterns:
        if pair.original.startswith('#'):
            table.add_row(pair.original, "")
        else:
            fossil_patterns = "\n".join(pair.converted) if pair.converted else ""
            table.add_row(pair.original, fossil_patterns)
    
    console.print(Panel.fit(
        "[bold]Pattern Conversion: .gitignore → Fossil[/]",
        border_style="blue"
    ))
    console.print(table)
    
    # Show the command to apply these patterns
    fossil_ignore = "\n".join(
        pattern
        for pair in patterns
        if not pair.original.startswith('#')
        for pattern in pair.converted
    )
    
    console.print(Panel(
        "[bold]To apply these patterns:[/]\n\n"
        "[cyan]mkdir -p .fossil-settings\n"
        "cat > .fossil-settings/ignore-glob << 'EOF'\n"
        f"{fossil_ignore}\n"
        "EOF\n"
        "fossil add .fossil-settings/ignore-glob\n"
        "fossil commit -m 'Add global ignore patterns'[/]",
        title="Next Steps",
        border_style="green"
    ))

def print_simple_comparison(patterns: List[PatternPair]) -> None:
    """Fallback display when rich is not available."""
    print("Pattern Conversion: .gitignore → Fossil")
    print("=" * 50)
    
    max_orig = max(len(pair.original) for pair in patterns) + 2
    format_str = f"{{:<{max_orig}}} | {{}}"
    
    print(format_str.format(".gitignore", "Fossil Ignore"))
    print("-" * (max_orig + 3) + "|" + "-" * 30)
    
    for pair in patterns:
        if pair.original.startswith('#'):
            print(pair.original)
        else:
            fossil_patterns = "\n" + " " * (max_orig + 3) + "| ".join(pair.converted)
            print(format_str.format(pair.original, fossil_patterns.lstrip()))
    
    print("\nTo apply these patterns:")
    print("""
mkdir -p .fossil-settings
cat > .fossil-settings/ignore-glob << 'EOF'""")
    for pair in patterns:
        if not pair.original.startswith('#'):
            for pattern in pair.converted:
                print(pattern)
    print("""EOF
fossil add .fossil-settings/ignore-glob
fossil commit -m 'Add global ignore patterns'""")

def main(gitignore_path: Optional[str] = None) -> None:
    """Main function to handle the conversion."""
    if gitignore_path is None:
        gitignore_path = '.gitignore'
        
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {gitignore_path} not found", file=sys.stderr)
        sys.exit(1)
        
    patterns = convert_gitignore_to_fossil(content)
    
    if RICH_AVAILABLE:
        print_rich_comparison(patterns)
    else:
        print("Tip: Install 'rich' for better output formatting: pip install rich")
        print_simple_comparison(patterns)

if __name__ == '__main__':
    gitignore_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(gitignore_file)
