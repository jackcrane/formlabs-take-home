import sys

class ProgressBar:
    def __init__(self, total, length=40, fill="█", empty="-", prefix="", suffix=""):
        self.total = total
        self.length = length
        self.fill = fill
        self.empty = empty
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0

    def update(self, step=1):
        self.current = min(self.current + step, self.total)
        self.render()

    def render(self):
        progress = self.current / self.total
        filled_len = int(self.length * progress)

        bar = self.fill * filled_len + self.empty * (self.length - filled_len)

        sys.stdout.write(
            f"\r{self.prefix} |{bar}| {progress * 100:6.2f}% {self.suffix}"
        )
        sys.stdout.flush()

        if self.current == self.total:
            self.finish()

    def finish(self):
        sys.stdout.write("\n")