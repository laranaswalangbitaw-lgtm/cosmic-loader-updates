#!/usr/bin/env python3
"""🎯 COSMIC COMBO GENERATOR — Auto-generate email:pass combos"""
import os, random, string, time
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich import box
except ImportError:
    os.system("pip install -q rich")
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich import box

console = Console()

FIRST_NAMES = ["juan", "maria", "jose", "ana", "carlo", "liza", "pedro", "rosa", "miguel", "sofia",
               "john", "jane", "mike", "sarah", "david", "emma", "alex", "lisa", "chris", "kate"]
LAST_NAMES = ["dela cruz", "santos", "reyes", "garcia", "mendoza", "torres", "flores", "ramos",
              "bautista", "aquino", "cruz", "villa", "castillo", "domingo", "navarro", "salazar"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com"]
PASSWORDS = ["123456", "password", "qwerty", "admin", "letmein", "welcome", "abc123", "monkey"]


class ComboGenerator:
    def __init__(self):
        self.output_dir = Path("/storage/emulated/0/COSMIC-LOADER-v4.0/Combo")
        self.output_dir.mkdir(exist_ok=True)

    def generate_email(self, style="name"):
        """Generate realistic email."""
        if style == "name":
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES).replace(" ", "")
            num = random.randint(1, 999)
            return f"{first}.{last}{num}@{random.choice(DOMAINS)}"
        elif style == "random":
            return f"{self._rand_str(10)}@{random.choice(DOMAINS)}"
        elif style == "simple":
            return f"{self._rand_str(8)}@{random.choice(DOMAINS)}"
        return f"{self._rand_str(10)}@gmail.com"

    def generate_password(self, style="weak"):
        """Generate password."""
        if style == "weak":
            return random.choice(PASSWORDS)
        elif style == "common":
            patterns = [
                lambda: f"{random.choice(FIRST_NAMES)}{random.randint(1, 999)}",
                lambda: f"{random.choice(FIRST_NAMES)}@{random.randint(1, 99)}",
                lambda: f"{random.randint(1000, 9999)}",
            ]
            return random.choice(patterns)()
        elif style == "strong":
            chars = string.ascii_letters + string.digits + "!@#$"
            return "".join(random.choice(chars) for _ in range(12))
        return self._rand_str(8)

    def _rand_str(self, n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

    def generate(self, count, style="mixed", output_file=None):
        """Generate combos."""
        if output_file is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"generated_{ts}.txt"

        combos = set()
        start = time.time()
        
        with console.status(f"[bold cyan]Generating {count:,} combos...", spinner="dots"):
            while len(combos) < count:
                if style == "mixed":
                    email_style = random.choice(["name", "random", "simple"])
                    pass_style = random.choice(["weak", "common", "strong"])
                else:
                    email_style = style
                    pass_style = "common"
                
                email = self.generate_email(email_style)
                password = self.generate_password(pass_style)
                combos.add(f"{email}:{password}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(combos)) + '\n')
        
        elapsed = time.time() - start
        return len(combos), output_file, elapsed


def run_combo_generator():
    """Main entry point."""
    console.clear()
    w = 66
    console.print(f"\n  [bold cyan]╭{'─' * w}╮[/bold cyan]")
    console.print(f"  [bold cyan]│[/bold cyan]{'[bold bright_cyan]◆  COMBO GENERATOR  ◆[/bold bright_cyan]'.center(w + 12)}[bold cyan]│[/bold cyan]")
    console.print(f"  [bold cyan]╰{'─' * w}╯[/bold cyan]\n")
    
    console.print("  [bold bright_cyan]Choose style:[/bold bright_cyan]")
    console.print("  [cyan][1][/cyan] Name-based (juan.delacruz123@gmail.com)")
    console.print("  [cyan][2][/cyan] Random (a8b2c9d1e0@gmail.com)")
    console.print("  [cyan][3][/cyan] Simple (user1234@gmail.com)")
    console.print("  [cyan][4][/cyan] Mixed (all styles)")
    console.print("  [cyan][0][/cyan] Back\n")
    
    choice = Prompt.ask("  [bold cyan]Pick[/bold cyan]").strip()
    
    if choice == '0':
        return
    
    styles = {'1': 'name', '2': 'random', '3': 'simple', '4': 'mixed'}
    style = styles.get(choice, 'mixed')
    
    count = IntPrompt.ask("  [cyan]How many?[/cyan] (e.g. 1000)", default=1000)
    if count <= 0 or count > 1000000:
        console.print("  [red]Invalid count. Max: 1,000,000[/red]")
        return
    
    gen = ComboGenerator()
    result_count, output_file, elapsed = gen.generate(count, style)
    
    console.print(f"\n  [bold green]✅ Generated {result_count:,} combos[/bold green]")
    console.print(f"  [dim]📁 {output_file}[/dim]")
    console.print(f"  [dim]⏱️  {elapsed:.2f}s ({result_count/elapsed:.0f}/s)[/dim]\n")
    input("  Press Enter...")
