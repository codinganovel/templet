#!/usr/bin/env python3
"""
templet - Simple Template Manager
A minimal TUI for managing text templates
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

# Try to import termios for advanced input handling
try:
    import termios
    import tty
    TERMIOS_AVAILABLE = True
except ImportError:
    TERMIOS_AVAILABLE = False

# ANSI color codes
class Color:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    CLEAR = '\033[2J\033[H'

# Supported text file extensions
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.html', '.css', '.yml', '.yaml', 
    '.json', '.xml', '.sh', '.bash', '.zsh', '.fish', '.toml', '.ini',
    '.cfg', '.conf', '.env', '.gitignore', '.dockerignore', '.rst',
    '.tex', '.csv', '.sql', '.vim', '.lua', '.rb', '.go', '.rs',
    '.java', '.c', '.cpp', '.h', '.hpp', '.php', '.swift', '.kt',
    '.r', '.R', '.jl', '.ts', '.tsx', '.jsx', '.vue', '.svelte',
    '.scss', '.sass', '.less', '.asm', '.s', '.pl', '.pm', '.tcl',
    '.dart', '.gradle', '.sbt', '.clj', '.cljs', '.edn', '.ex', '.exs',
    '.elm', '.fs', '.fsx', '.fsi', '.ml', '.mli', '.nim', '.nims',
    '.hx', '.hxml', '.pas', '.pp', '.inc', '.zig', '.v', '.vsh'
}

# Files with no extension that are text-based
NO_EXT_FILES = {
    'Dockerfile', '.gitignore', 'Makefile', 'Rakefile', 'Gemfile', 'Pipfile',
    'Procfile', 'Vagrantfile', 'Brewfile', 'Guardfile', 'Capfile',
    'Thorfile', 'Berksfile', 'Appraisals', 'Fastfile', 'Appfile',
    'Deliverfile', 'Matchfile', 'Scanfile', 'Gymfile', 'LICENSE',
    'README', 'CHANGELOG', 'AUTHORS', 'CONTRIBUTORS', 'COPYING',
    'INSTALL', 'NEWS', 'THANKS', 'HISTORY', 'NOTICE', 'MANIFEST'
}

class TemplateManager:
    def __init__(self):
        self.template_dir = Path.home() / 'Documents' / 'templet'
        self.templates: List[str] = []
        self.selected_index = 0
        self.use_termios = TERMIOS_AVAILABLE
        self.setup_directory()
        self.load_templates()
    
    def setup_directory(self):
        """Create template directory if it doesn't exist"""
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def is_supported_file(self, filepath: Path) -> bool:
        """Check if file is a supported text format"""
        # Check if it's a known no-extension text file
        if filepath.name in NO_EXT_FILES:
            return True
        
        # Check if it has a supported extension
        return filepath.suffix.lower() in TEXT_EXTENSIONS
    
    def load_templates(self):
        """Load all supported templates from the directory"""
        self.templates = sorted([
            f.name for f in self.template_dir.iterdir() 
            if f.is_file() and self.is_supported_file(f)
        ])
    
    def get_key_termios(self) -> str:
        """Get a single keypress from the user using termios"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            # Handle arrow keys (they send escape sequences)
            if key == '\x1b':
                key += sys.stdin.read(2)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def get_command_fallback(self) -> str:
        """Get command input for systems without termios"""
        if not self.templates:
            command = input(f"{Color.CYAN}Command (q=quit): {Color.RESET}").strip().lower()
        else:
            print(f"{Color.DIM}Commands: up/u, down/d, 1-{min(9, len(self.templates))}, enter/e (with date), copy/c (no date), quit/q{Color.RESET}")
            command = input(f"{Color.CYAN}Command [current: {self.selected_index + 1}]: {Color.RESET}").strip().lower()
        return command
    
    def draw_ui(self):
        """Draw the TUI interface"""
        # Clear screen and move cursor to top
        print(Color.CLEAR, end='')
        
        # Calculate dimensions
        width = 44
        
        # Top border
        print(f"{Color.BLUE}╔{'═' * (width - 2)}╗{Color.RESET}")
        
        # Title
        mode_indicator = " [fancy]" if self.use_termios else " [not-fancy]"
        title = f"templet {mode_indicator}"
        padding = (width - len(title) - 2) // 2
        print(f"{Color.BLUE}║{Color.RESET}{' ' * padding}{Color.BOLD}{Color.CYAN}{title}{Color.RESET}{' ' * (width - padding - len(title) - 2)}{Color.BLUE}║{Color.RESET}")
        
        # Separator
        print(f"{Color.BLUE}╠{'═' * (width - 2)}╣{Color.RESET}")
        
        # Template directory
        dir_text = f"Templates: ~/Documents/templet/"
        padding = (width - len(dir_text) - 2) // 2
        print(f"{Color.BLUE}║{Color.RESET}{' ' * padding}{Color.DIM}{dir_text}{Color.RESET}{' ' * (width - padding - len(dir_text) - 2)}{Color.BLUE}║{Color.RESET}")
        
        # Separator
        print(f"{Color.BLUE}╠{'═' * (width - 2)}╣{Color.RESET}")
        
        # Content area (10 lines)
        content_height = 10
        if not self.templates:
            # No templates message
            empty_lines = [
                "",
                "     No templates found!",
                "",
                "  Add files to: ~/Documents/templet/",
                "",
                "  Supported: .txt .md .py .yml .json",
                "  .sh .html .toml .env Dockerfile ...",
                ""
            ]
            for i in range(content_height):
                if i < len(empty_lines):
                    line = empty_lines[i]
                    print(f"{Color.BLUE}║{Color.RESET}{line}{' ' * (width - len(line) - 2)}{Color.BLUE}║{Color.RESET}")
                else:
                    print(f"{Color.BLUE}║{Color.RESET}{' ' * (width - 2)}{Color.BLUE}║{Color.RESET}")
        else:
            # Show templates with selection
            start_idx = max(0, min(self.selected_index - 4, len(self.templates) - content_height))
            end_idx = start_idx + content_height
            
            for i in range(content_height):
                if start_idx + i < len(self.templates):
                    template = self.templates[start_idx + i]
                    item_number = start_idx + i + 1
                    
                    if start_idx + i == self.selected_index:
                        # Selected item
                        if self.use_termios:
                            line = f"  {Color.CYAN}→ {Color.BOLD}{template}{Color.RESET}"
                        else:
                            line = f" {Color.CYAN}[{item_number}] {Color.BOLD}{template}{Color.RESET}"
                        # Calculate remaining space more carefully
                        line_length = len(f"  → {template}") if self.use_termios else len(f" [{item_number}] {template}")
                        print(f"{Color.BLUE}║{Color.RESET}{line}{' ' * (width - line_length - 2)}{Color.BLUE}║{Color.RESET}")
                    else:
                        # Normal item
                        if self.use_termios:
                            line = f"    {template}"
                        else:
                            line = f"  [{item_number}] {template}"
                        print(f"{Color.BLUE}║{Color.RESET}{line}{' ' * (width - len(line) - 2)}{Color.BLUE}║{Color.RESET}")
                else:
                    print(f"{Color.BLUE}║{Color.RESET}{' ' * (width - 2)}{Color.BLUE}║{Color.RESET}")
        
        # Bottom separator
        print(f"{Color.BLUE}╠{'═' * (width - 2)}╣{Color.RESET}")
        
        # Controls
        if self.templates:
            if self.use_termios:
                controls = "  ↑↓ Navigate │ Enter: +Date │ c: Copy │ q: Quit  "
            else:
                controls = "  Type commands below (help shown)  "
        else:
            controls = "  q: Quit  "
        padding = (width - len(controls) - 2) // 2
        print(f"{Color.BLUE}║{Color.RESET}{' ' * padding}{Color.DIM}{controls}{Color.RESET}{' ' * (width - padding - len(controls) - 2)}{Color.BLUE}║{Color.RESET}")
        
        # Bottom border
        print(f"{Color.BLUE}╚{'═' * (width - 2)}╝{Color.RESET}")
    
    def create_file_from_template(self, template_name: str, add_date_prefix: bool = True) -> str:
        """Create a new file from the selected template"""
        # Read template content
        template_path = self.template_dir / template_name
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract base name and extension
        if '.' in template_name:
            base_name, extension = template_name.rsplit('.', 1)
            extension = '.' + extension
        else:
            base_name = template_name
            extension = ''
        
        # Generate filename
        if add_date_prefix:
            date_prefix = datetime.now().strftime('%Y-%m-%d')
            new_filename = f"{date_prefix}-{base_name}{extension}"
        else:
            new_filename = f"{base_name}{extension}"
        
        # Handle file conflicts
        counter = 1
        original_filename = new_filename
        while Path(new_filename).exists():
            if '.' in original_filename:
                name_part, ext_part = original_filename.rsplit('.', 1)
                new_filename = f"{name_part}-{counter}.{ext_part}"
            else:
                new_filename = f"{original_filename}-{counter}"
            counter += 1
        
        # Check if this file type should get a header
        header_safe_extensions = {'.txt', '.md', '.markdown', '.mdown', '.mkd'}
        
        if extension.lower() in header_safe_extensions and add_date_prefix:
            # Create header for text/markdown files (only when date prefix is used)
            header = f"""# ✦ Template: {template_name}
### 📅 {datetime.now().strftime('%Y-%m-%d • %H:%M:%S')}
---

"""
            final_content = header + content
        else:
            # Copy as-is for all other file types or when no date prefix
            final_content = content
        
        # Write new file
        with open(new_filename, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return new_filename
    
    def handle_fallback_command(self, command: str) -> bool:
        """Handle text-based commands for systems without termios. Returns True to continue, False to exit."""
        if not command:
            command = 'enter'  # Default to enter when empty
        
        if command in ['q', 'quit', 'exit']:
            return False
        elif command in ['up', 'u'] and self.templates:
            self.selected_index = max(0, self.selected_index - 1)
        elif command in ['down', 'd'] and self.templates:
            self.selected_index = min(len(self.templates) - 1, self.selected_index + 1)
        elif command.isdigit() and self.templates:
            # Jump to numbered item (1-based)
            target_index = int(command) - 1
            if 0 <= target_index < len(self.templates):
                self.selected_index = target_index
        elif command in ['enter', 'e', ''] and self.templates:
            # Create with date prefix
            template = self.templates[self.selected_index]
            filename = self.create_file_from_template(template, add_date_prefix=True)
            print(Color.CLEAR, end='')
            print(f"{Color.CYAN}✓ Created: {Color.BOLD}{filename}{Color.RESET}")
            return False
        elif command in ['copy', 'c'] and self.templates:
            # Create without date prefix
            template = self.templates[self.selected_index]
            filename = self.create_file_from_template(template, add_date_prefix=False)
            print(Color.CLEAR, end='')
            print(f"{Color.CYAN}✓ Created: {Color.BOLD}{filename}{Color.RESET}")
            return False
        elif command in ['help', 'h', '?']:
            print(f"\n{Color.CYAN}Available commands:{Color.RESET}")
            print(f"  {Color.BOLD}up, u{Color.RESET} - Move selection up")
            print(f"  {Color.BOLD}down, d{Color.RESET} - Move selection down")
            print(f"  {Color.BOLD}1-9{Color.RESET} - Jump to numbered item")
            print(f"  {Color.BOLD}enter, e{Color.RESET} - Create file with date prefix")
            print(f"  {Color.BOLD}copy, c{Color.RESET} - Create file without date prefix")
            print(f"  {Color.BOLD}quit, q{Color.RESET} - Exit program")
            print(f"  {Color.BOLD}help, h{Color.RESET} - Show this help")
            input(f"\n{Color.DIM}Press Enter to continue...{Color.RESET}")
        else:
            if self.templates:
                print(f"{Color.DIM}Unknown command. Try: up/down, 1-{min(9, len(self.templates))}, enter, copy, quit, help{Color.RESET}")
            else:
                print(f"{Color.DIM}Unknown command. Try: quit{Color.RESET}")
            input(f"{Color.DIM}Press Enter to continue...{Color.RESET}")
        
        return True
    
    def run(self):
        """Main TUI loop"""
        try:
            while True:
                self.draw_ui()
                
                if self.use_termios:
                    # Original termios-based input handling
                    key = self.get_key_termios()
                    
                    if key == 'q':
                        break
                    elif key == '\x1b[A' and self.templates:  # Up arrow
                        self.selected_index = max(0, self.selected_index - 1)
                    elif key == '\x1b[B' and self.templates:  # Down arrow
                        self.selected_index = min(len(self.templates) - 1, self.selected_index + 1)
                    elif key == '\r' and self.templates:  # Enter - with date prefix
                        template = self.templates[self.selected_index]
                        filename = self.create_file_from_template(template, add_date_prefix=True)
                        print(Color.CLEAR, end='')
                        print(f"{Color.CYAN}✓ Created: {Color.BOLD}{filename}{Color.RESET}")
                        break
                    elif key == 'c' and self.templates:  # c - copy without date
                        template = self.templates[self.selected_index]
                        filename = self.create_file_from_template(template, add_date_prefix=False)
                        print(Color.CLEAR, end='')
                        print(f"{Color.CYAN}✓ Created: {Color.BOLD}{filename}{Color.RESET}")
                        break
                else:
                    # Fallback text-based input handling
                    command = self.get_command_fallback()
                    if not self.handle_fallback_command(command):
                        break
                        
        except KeyboardInterrupt:
            pass
        finally:
            # Clear any formatting
            print(Color.RESET, end='')

def main():
    """Entry point"""
    manager = TemplateManager()
    manager.run()

if __name__ == '__main__':
    main()