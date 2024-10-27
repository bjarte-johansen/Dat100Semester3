import time

class Timer:
    def __init__(self, title:str, start_timer:bool=False):
        self.title = title
        self.start_time = None
        self.end_time = None
        self.elapsed = None
        if start_timer:
            self.start()

    def start(self):
        """Start the timer."""
        self.start_time = time.perf_counter()
        self.end_time = None
        self.elapsed = None
        #print(f"Timer started {self.title}...")

    def stop(self):
        """Stop the timer and calculate the elapsed time."""
        if self.start_time is None:
            print("Timer has not been started.")
            return

        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        print(f"{self.elapsed:.4f} seconds for {self.title}")

    def get_elapsed(self):
        """Get the elapsed time without stopping the timer."""
        if self.start_time is None:
            print("Timer has not been started.")
            return None

        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time
        print(f"Elapsed time so far: {elapsed_time:.4f} seconds")
        return elapsed_time

    def reset(self):
        """Reset the timer."""
        self.start_time = None
        self.end_time = None
        self.elapsed = None
        print("Timer reset.")