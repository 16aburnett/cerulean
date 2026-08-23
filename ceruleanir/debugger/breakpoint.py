# CeruleanIR Debugger - Breakpoint Management
# Author: Amy Burnett
# =================================================================================================

from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Breakpoint:
    """Represents a breakpoint in the debugger."""
    id: int
    location: str  # Format: @function[.block[.index]]
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    
    def matches(self, location: str) -> bool:
        """Check if this breakpoint matches the given location."""
        # Exact match
        if self.location == location:
            return True
        
        # Prefix match (e.g., breakpoint at @main matches @main.entry.5)
        if location.startswith(self.location + '.'):
            return True
        
        return False

class BreakpointManager:
    """Manages breakpoints for the debugger."""
    
    def __init__(self):
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.next_id = 1
    
    def add_breakpoint(self, location: str, condition: Optional[str] = None) -> int:
        """
        Add a new breakpoint.
        Returns the breakpoint ID.
        """
        bp_id = self.next_id
        self.next_id += 1
        
        bp = Breakpoint(
            id=bp_id,
            location=location,
            condition=condition,
            enabled=True
        )
        
        self.breakpoints[bp_id] = bp
        return bp_id
    
    def delete_breakpoint(self, bp_id: int) -> bool:
        """Delete a breakpoint by ID. Returns True if found."""
        if bp_id in self.breakpoints:
            del self.breakpoints[bp_id]
            return True
        return False
    
    def enable_breakpoint(self, bp_id: int) -> bool:
        """Enable a breakpoint by ID. Returns True if found."""
        if bp_id in self.breakpoints:
            self.breakpoints[bp_id].enabled = True
            return True
        return False
    
    def disable_breakpoint(self, bp_id: int) -> bool:
        """Disable a breakpoint by ID. Returns True if found."""
        if bp_id in self.breakpoints:
            self.breakpoints[bp_id].enabled = False
            return True
        return False
    
    def should_break_at(self, location: str, context) -> bool:
        """
        Check if we should break at the given location.
        Considers breakpoint matching, enabled state, and conditions.
        """
        for bp in self.breakpoints.values():
            if not bp.enabled:
                continue
            
            if bp.matches(location):
                # Check condition if present
                if bp.condition:
                    # TODO: Evaluate condition against context
                    # For now, just break unconditionally
                    pass
                
                bp.hit_count += 1
                return True
        
        return False
    
    def list_breakpoints(self):
        """Print all breakpoints."""
        if not self.breakpoints:
            print("No breakpoints set")
            return
        
        print("Breakpoints:")
        for bp_id, bp in sorted(self.breakpoints.items()):
            status = "enabled" if bp.enabled else "disabled"
            cond_str = f" if {bp.condition}" if bp.condition else ""
            hits_str = f" (hit {bp.hit_count} time{'s' if bp.hit_count != 1 else ''})" if bp.hit_count > 0 else ""
            print(f"  {bp.id}: {bp.location}{cond_str} [{status}]{hits_str}")
