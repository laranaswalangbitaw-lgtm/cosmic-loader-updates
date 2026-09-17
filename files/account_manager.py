#!/usr/bin/env python3
"""📊 COSMIC ACCOUNT MANAGER — Results Dashboard"""
import os, json, csv, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.align import Align
    from rich import box
except ImportError:
    os.system("pip install -q rich")
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.align import Align
    from rich import box

console = Console()

_RE_LEVEL = re.compile(r'Account Level:\s*(\d+)')
_RE_SHELL = re.compile(r'Garena Shell:\s*(\d+)')
_RE_REGION = re.compile(r'Server:\s*(.+?)(?:\n|$)', re.IGNORECASE)
_RE_IGN = re.compile(r'IGN:\s*(.+?)(?:\n|$)', re.IGNORECASE)


class AccountManager:
    def __init__(self):
        self.results_dir = Path("/storage/emulated/0/COSMIC-LOADER-v4.0/Results")
        self.results_dir.mkdir(exist_ok=True)
        self.accounts = []
        self.stats = defaultdict(int)

    def parse_file(self, filepath):
        """Parse results file."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []
        
        accounts = []
        blocks = re.split(r'={60}', content)
        
        for block in blocks:
            block = block.strip()
            if not block or 'Account:' not in block:
                continue
            
            acc = {'raw': block, 'file': filepath.name}
            
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith('Account:'):
                    acc['login'] = line.replace('Account:', '').strip()
                elif line.startswith('UID:'):
                    acc['uid'] = line.replace('UID:', '').strip()
                elif line.startswith('Username:'):
                    acc['username'] = line.replace('Username:', '').strip()
                elif line.startswith('Country:'):
                    acc['country'] = line.replace('Country:', '').strip()
                elif line.startswith('Account Level:'):
                    try: acc['level'] = int(line.replace('Account Level:', '').strip())
                    except: acc['level'] = 0
                elif line.startswith('Garena Shell:'):
                    try: acc['shell'] = int(line.replace('Garena Shell:', '').strip())
                    except: acc['shell'] = 0
                elif line.startswith('Server:'):
                    acc['region'] = line.replace('Server:', '').strip()
                elif line.startswith('IGN:'):
                    acc['ign'] = line.replace('IGN:', '').strip()
                elif line.startswith('Account Status:'):
                    acc['status'] = line.replace('Account Status:', '').strip()
                elif line.startswith('Email:'):
                    acc['email'] = line.replace('Email:', '').strip()
                elif line.startswith('Mobile:'):
                    acc['mobile'] = line.replace('Mobile:', '').strip()
            
            accounts.append(acc)
        
        return accounts

    def load_all(self):
        """Load all result files."""
        self.accounts = []
        files = list(self.results_dir.glob("**/*.txt"))
        
        for f in files:
            accounts = self.parse_file(f)
            self.accounts.extend(accounts)
        
        self._compute_stats()
        return len(self.accounts)

    def _compute_stats(self):
        """Compute statistics."""
        self.stats = defaultdict(int)
        self.stats['total'] = len(self.accounts)
        
        for a in self.accounts:
            if a.get('status') == 'Clean':
                self.stats['clean'] += 1
            else:
                self.stats['not_clean'] += 1
            
            if a.get('level', 0) >= 100:
                self.stats['high_level'] += 1
            
            if a.get('shell', 0) > 0:
                self.stats['has_shell'] += 1
            
            region = a.get('region', '').split()[-1] if a.get('region') else 'N/A'
            self.stats[f'region_{region}'] += 1

    def display_stats(self):
        """Display dashboard stats."""
        console.clear()
        w = 66
        console.print(f"\n  [bold cyan]╭{'─' * w}╮[/bold cyan]")
        console.print(f"  [bold cyan]│[/bold cyan]{'[bold bright_cyan]◆  ACCOUNT MANAGER  ◆[/bold bright_cyan]'.center(w + 12)}[bold cyan]│[/bold cyan]")
        console.print(f"  [bold cyan]╰{'─' * w}╯[/bold cyan]\n")

        table = Table(box=box.ROUNDED, border_style="cyan", show_header=False, padding=(0, 2))
        table.add_column("Metric", style="dim", width=20)
        table.add_column("Value", style="bright_white", width=15)
        table.add_column("Bar", width=25)

        total = max(self.stats['total'], 1)
        for label, key, color in [
            ('📊 Total', 'total', 'bright_cyan'),
            ('✨ Clean', 'clean', 'bright_green'),
            ('⊘ Not Clean', 'not_clean', 'bright_yellow'),
            ('⭐ High Level', 'high_level', 'bright_magenta'),
            ('💎 Has Shell', 'has_shell', 'gold1'),
        ]:
            val = self.stats.get(key, 0)
            bar = self._mini_bar(val, total, color)
            table.add_row(label, f"{val:,}", bar)

        console.print(table)

    def _mini_bar(self, count, denom, color, width=22):
        if denom == 0:
            return Text("░" * width, style="dim")
        ratio = min(count / denom, 1.0)
        filled = int(ratio * width)
        bar = Text()
        bar.append("█" * filled, style=color)
        bar.append("░" * (width - filled), style="dim")
        return bar

    def search(self, query):
        """Search accounts."""
        q = query.lower()
        results = []
        for a in self.accounts:
            if (q in a.get('login', '').lower() or 
                q in a.get('username', '').lower() or
                q in a.get('uid', '').lower() or
                q in a.get('ign', '').lower()):
                results.append(a)
        return results

    def filter_accounts(self, filter_type):
        """Filter accounts."""
        results = []
        for a in self.accounts:
            if filter_type == 'clean' and a.get('status') == 'Clean':
                results.append(a)
            elif filter_type == 'not_clean' and a.get('status') != 'Clean':
                results.append(a)
            elif filter_type == 'high_level' and a.get('level', 0) >= 100:
                results.append(a)
            elif filter_type == 'has_shell' and a.get('shell', 0) > 0:
                results.append(a)
        return results

    def export_csv(self, accounts, output_path):
        """Export to CSV."""
        if not accounts:
            return False
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['login', 'uid', 'username', 'country', 'level', 'shell', 'region', 'ign', 'status'])
                writer.writeheader()
                for a in accounts:
                    writer.writerow({k: a.get(k, '') for k in writer.fieldnames})
            return True
        except Exception:
            return False


def run_account_manager():
    """Main entry point."""
    manager = AccountManager()
    
    with console.status("[bold cyan]Loading accounts...", spinner="dots"):
        total = manager.load_all()
    
    if total == 0:
        console.print("\n[bold yellow]⚠  No accounts found in Results/[/bold yellow]")
        console.print("[dim]Run Bulk Check first to generate results.[/dim]\n")
        input("  Press Enter...")
        return
    
    while True:
        manager.display_stats()
        
        console.print(f"\n  [bold bright_cyan]Options:[/bold bright_cyan]")
        console.print(f"  [cyan][1][/cyan] 🔍 Search accounts")
        console.print(f"  [cyan][2][/cyan] ✨ Show Clean only")
        console.print(f"  [cyan][3][/cyan] ⊘ Show Not Clean only")
        console.print(f"  [cyan][4][/cyan] ⭐ Show High Level (100+)")
        console.print(f"  [cyan][5][/cyan] 💎 Show With Shell Balance")
        console.print(f"  [cyan][6][/cyan] 📤 Export to CSV")
        console.print(f"  [cyan][0][/cyan] 🚪 Back\n")
        
        choice = Prompt.ask("  [bold cyan]Pick[/bold cyan]").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            q = Prompt.ask("  [cyan]Search[/cyan]").strip()
            results = manager.search(q)
            _show_results(results, f"Search: {q}")
        elif choice == '2':
            _show_results(manager.filter_accounts('clean'), "Clean Accounts")
        elif choice == '3':
            _show_results(manager.filter_accounts('not_clean'), "Not Clean Accounts")
        elif choice == '4':
            _show_results(manager.filter_accounts('high_level'), "High Level (100+)")
        elif choice == '5':
            _show_results(manager.filter_accounts('has_shell'), "With Shell Balance")
        elif choice == '6':
            accounts = manager.accounts
            out = manager.results_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            if manager.export_csv(accounts, out):
                console.print(f"\n  [bold green]✅ Exported: {out}[/bold green]\n")
            else:
                console.print(f"\n  [red]❌ Export failed[/red]\n")
            input("  Press Enter...")


def _show_results(accounts, title):
    """Show accounts in table."""
    console.clear()
    console.print(f"\n  [bold bright_cyan]═══ {title} ({len(accounts)}) ═══[/bold bright_cyan]\n")
    
    if not accounts:
        console.print("  [dim]No accounts found.[/dim]\n")
        input("  Press Enter...")
        return
    
    table = Table(box=box.ROUNDED, border_style="cyan", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Login", style="bright_white", width=28)
    table.add_column("Level", style="bright_magenta", width=6)
    table.add_column("Shell", style="gold1", width=8)
    table.add_column("Region", style="bright_cyan", width=12)
    table.add_column("Status", width=10)
    
    for i, a in enumerate(accounts[:30], 1):
        status = a.get('status', 'N/A')
        s_color = "bright_green" if status == 'Clean' else "bright_yellow"
        table.add_row(
            str(i),
            a.get('login', 'N/A')[:26],
            str(a.get('level', 0)),
            f"{a.get('shell', 0):,}",
            a.get('region', 'N/A')[:10],
            f"[{s_color}]{status}[/{s_color}]"
        )
    
    console.print(table)
    if len(accounts) > 30:
        console.print(f"\n  [dim]... +{len(accounts) - 30} more[/dim]")
    console.print()
    input("  Press Enter...")
