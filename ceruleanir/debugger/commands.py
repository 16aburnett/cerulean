# CeruleanIR Debugger - Command Parser and Handlers
# Author: Amy Burnett
# =================================================================================================

import shlex

class CommandParser:
    """
    Parses and executes debugger commands.
    """
    
    def __init__(self, debugger):
        self.debugger = debugger
        
        # Command registry: name -> (handler, help_text, aliases)
        self.commands = {
            'help': (self.cmd_help, 'Show help for commands', ['h', '?']),
            'quit': (self.cmd_quit, 'Exit the debugger', ['q', 'exit']),
            'run': (self.cmd_run, 'Start or restart program execution', ['r']),
            'continue': (self.cmd_continue, 'Continue execution until breakpoint', ['c', 'cont']),
            'step': (self.cmd_step, 'Step one instruction (into calls)', ['s']),
            'next': (self.cmd_next, 'Step one instruction (over calls)', ['n']),
            'finish': (self.cmd_finish, 'Run until current function returns', ['fin']),
            'break': (self.cmd_break, 'Set breakpoint: break @function[.block[.index]]', ['b']),
            'delete': (self.cmd_delete, 'Delete breakpoint: delete <n>', ['d']),
            'disable': (self.cmd_disable, 'Disable breakpoint: disable <n>', []),
            'enable': (self.cmd_enable, 'Enable breakpoint: enable <n>', []),
            'info': (self.cmd_info, 'Show information: info <what>', ['i']),
            'print': (self.cmd_print, 'Print variable: print <var>', ['p']),
            'list': (self.cmd_list, 'Show current location and context', ['l']),
            'where': (self.cmd_where, 'Show call stack', ['bt', 'backtrace']),
        }
        
        # Build alias map
        self.aliases = {}
        for cmd_name, (handler, help_text, aliases) in self.commands.items():
            for alias in aliases:
                self.aliases[alias] = cmd_name
    
    def execute(self, line):
        """
        Parse and execute a command line.
        Returns True if should quit, False otherwise.
        """
        # Parse command line
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"Parse error: {e}")
            return False
        
        if not parts:
            return False
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Resolve aliases
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
        
        # Execute command
        if cmd in self.commands:
            handler, _, _ = self.commands[cmd]
            return handler(args)
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for list of commands")
            return False
    
    # ========================================================================
    # Command Handlers
    # ========================================================================
    
    def cmd_help(self, args):
        """Show help for commands."""
        if args:
            # Help for specific command
            cmd = args[0].lower()
            if cmd in self.aliases:
                cmd = self.aliases[cmd]
            if cmd in self.commands:
                _, help_text, aliases = self.commands[cmd]
                print(f"{cmd}: {help_text}")
                if aliases:
                    print(f"  Aliases: {', '.join(aliases)}")
            else:
                print(f"Unknown command: {cmd}")
        else:
            # General help
            print("Available commands:")
            print()
            for cmd_name in sorted(self.commands.keys()):
                _, help_text, aliases = self.commands[cmd_name]
                alias_str = f" ({', '.join(aliases)})" if aliases else ""
                print(f"  {cmd_name}{alias_str}")
                print(f"    {help_text}")
        return False
    
    def cmd_quit(self, args):
        """Exit the debugger."""
        return True
    
    def cmd_run(self, args):
        """Start or restart program execution."""
        self.debugger.run()
        return False
    
    def cmd_continue(self, args):
        """Continue execution until breakpoint."""
        self.debugger.continue_execution()
        return False
    
    def cmd_step(self, args):
        """Step N instructions (into calls)."""
        count = int(args[0]) if args else 1
        self.debugger.step(count, into_calls=True)
        return False
    
    def cmd_next(self, args):
        """Step N instructions (over calls)."""
        count = int(args[0]) if args else 1
        self.debugger.step(count, into_calls=False)
        return False
    
    def cmd_finish(self, args):
        """Run until current function returns."""
        self.debugger.finish()
        return False
    
    def cmd_break(self, args):
        """Set a breakpoint."""
        if not args:
            # List breakpoints
            self.debugger.breakpoints.list_breakpoints()
            return False
        
        location = args[0]
        condition = ' '.join(args[1:]) if len(args) > 1 else None
        
        bp_id = self.debugger.breakpoints.add_breakpoint(location, condition)
        print(f"Breakpoint {bp_id} set at {location}")
        if condition:
            print(f"  Condition: {condition}")
        return False
    
    def cmd_delete(self, args):
        """Delete a breakpoint."""
        if not args:
            print("Usage: delete <breakpoint-number>")
            return False
        
        try:
            bp_id = int(args[0])
            if self.debugger.breakpoints.delete_breakpoint(bp_id):
                print(f"Deleted breakpoint {bp_id}")
            else:
                print(f"No breakpoint number {bp_id}")
        except ValueError:
            print("Breakpoint number must be an integer")
        return False
    
    def cmd_disable(self, args):
        """Disable a breakpoint."""
        if not args:
            print("Usage: disable <breakpoint-number>")
            return False
        
        try:
            bp_id = int(args[0])
            if self.debugger.breakpoints.disable_breakpoint(bp_id):
                print(f"Disabled breakpoint {bp_id}")
            else:
                print(f"No breakpoint number {bp_id}")
        except ValueError:
            print("Breakpoint number must be an integer")
        return False
    
    def cmd_enable(self, args):
        """Enable a breakpoint."""
        if not args:
            print("Usage: enable <breakpoint-number>")
            return False
        
        try:
            bp_id = int(args[0])
            if self.debugger.breakpoints.enable_breakpoint(bp_id):
                print(f"Enabled breakpoint {bp_id}")
            else:
                print(f"No breakpoint number {bp_id}")
        except ValueError:
            print("Breakpoint number must be an integer")
        return False
    
    def cmd_info(self, args):
        """Show information."""
        if not args:
            print("Usage: info <what>")
            print("  info breakpoints - List all breakpoints")
            print("  info locals      - Show local variables")
            print("  info globals     - Show global variables")
            return False
        
        what = args[0].lower()
        
        if what in ('breakpoints', 'break', 'b'):
            self.debugger.breakpoints.list_breakpoints()
        elif what in ('locals', 'local'):
            self.debugger.info_locals()
        elif what in ('globals', 'global'):
            self.debugger.info_globals()
        else:
            print(f"Unknown info command: {what}")
        return False
    
    def cmd_print(self, args):
        """Print a variable."""
        if not args:
            print("Usage: print <variable>")
            return False
        
        var_name = args[0]
        self.debugger.print_variable(var_name)
        return False
    
    def cmd_list(self, args):
        """Show current location and context."""
        self.debugger.show_context()
        return False
    
    def cmd_where(self, args):
        """Show call stack."""
        self.debugger.show_call_stack()
        return False
