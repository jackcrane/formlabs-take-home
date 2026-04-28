import sys
import time

class ProgressBar:
    def __init__(self, total, length=40, fill="█", empty="-", prefix="", suffix=""):
        self.total = total
        self.length = length
        self.fill = fill
        self.empty = empty
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.is_finished = False

    def update(self, step=1):
        self.current = min(self.current + step, self.total)
        self.render()

    def set_progress(self, progress):
        bounded_progress = max(0.0, min(float(progress), 1.0))
        self.current = bounded_progress * self.total
        self.render()

    def render(self):
        progress = self.current / self.total
        filled_len = int(self.length * progress)

        bar = self.fill * filled_len + self.empty * (self.length - filled_len)

        sys.stdout.write(
            f"\r{self.prefix} |{bar}| {progress * 100:6.2f}% {self.suffix}"
        )
        sys.stdout.flush()

        if self.current == self.total and not self.is_finished:
            self.finish()

    def finish(self):
        self.is_finished = True
        sys.stdout.write("\n")
        sys.stdout.flush()


def progressBarFromOperation(preform, prefix, operationId, startAt=0.0):
    progress_bar = ProgressBar(total=1, prefix=prefix, suffix="Complete")
    progress_bar.render()
    time.sleep(0.25)

    while True:
        operation = preform.api.get_operation(operationId)
        raw_progress = max(0.0, min(float(operation.progress or 0.0), 1.0))
        bounded_start_at = max(0.0, min(float(startAt), 1.0))

        if raw_progress <= bounded_start_at:
            normalized_progress = 0.0
        elif bounded_start_at >= 1.0:
            normalized_progress = 1.0 if operation.status == "SUCCEEDED" else 0.0
        else:
            normalized_progress = (raw_progress - bounded_start_at) / (1.0 - bounded_start_at)

        progress_bar.set_progress(normalized_progress)

        if operation.status == "SUCCEEDED":
            return operation

        if operation.status == "FAILED":
            raise RuntimeError(
                f"{prefix.strip()} failed: {operation.result}"
            )

        time.sleep(0.25)
