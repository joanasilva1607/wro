"""
Lane and LaneTraffic classes for obstacle challenge navigation.
"""

class LaneTraffic:
    """Enumeration for lane traffic positions."""
    Inside = "inside"
    Outside = "outside"
    Unknown = "unknown"


class Lane:
    """Represents a lane with initial and final traffic positions."""
    
    def __init__(self, initial=LaneTraffic.Unknown, final=LaneTraffic.Unknown):
        """
        Initialize a lane.
        
        Args:
            initial: Initial traffic position when entering the lane
            final: Final traffic position when exiting the lane
        """
        self.initial = initial
        self.final = final
        
    def __str__(self):
        """String representation of the lane."""
        return f"Lane(initial={self.initial}, final={self.final})"
        
    def __repr__(self):
        """Detailed string representation of the lane."""
        return f"Lane(initial={self.initial}, final={self.final})"
        
    def is_obstacle_present(self):
        """
        Check if there's an obstacle in this lane.
        
        Returns:
            bool: True if there's an obstacle (position is not Unknown)
        """
        return self.initial != LaneTraffic.Unknown or self.final != LaneTraffic.Unknown
        
    def has_position_change(self):
        """
        Check if the traffic position changes within this lane.
        
        Returns:
            bool: True if initial and final positions are different
        """
        return self.initial != self.final
        
    def get_obstacle_side(self):
        """
        Get the side where the obstacle is located.
        
        Returns:
            LaneTraffic: The side where the obstacle is located, or Unknown if no obstacle
        """
        if self.initial != LaneTraffic.Unknown:
            return self.initial
        elif self.final != LaneTraffic.Unknown:
            return self.final
        else:
            return LaneTraffic.Unknown
