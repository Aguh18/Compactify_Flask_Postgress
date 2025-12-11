"""
Memory optimization utilities for Compactify application
"""

import gc
import time
import threading

# Global memory optimization lock
_memory_lock = threading.Lock()

def force_garbage_collect():
    """Force garbage collection to free memory"""
    with _memory_lock:
        try:
            gc.collect()
        except Exception as e:
            print(f"Error during garbage collection: {e}")

def optimize_memory_heavy_operations(func):
    """Decorator for memory-intensive operations"""
    def wrapper(*args, **kwargs):
        try:
            # Pre-operation cleanup
            force_garbage_collect()

            # Execute the function
            result = func(*args, **kwargs)

            # Post-operation cleanup
            force_garbage_collect()

            return result

        except Exception as e:
            # Cleanup even on error
            force_garbage_collect()
            raise e

    return wrapper

def cleanup_after_processing():
    """Standard cleanup after file processing operations"""
    force_garbage_collect()
    time.sleep(0.1)  # Small delay to allow cleanup
    force_garbage_collect()  # Second cleanup for thoroughness