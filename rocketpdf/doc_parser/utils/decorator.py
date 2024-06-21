from functools import wraps
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console

console = Console()


def spinner(
    task_description: str = "Processing...",
    success_message: str = "Succesfully completed",
    error_message: str = "An error ocurred",
) -> wraps:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(task_description, total=None)
                try:
                    result = func(*args, **kwargs)
                    progress.update(task, advance=1, visible=False)
                    progress.stop()
                    console.print(
                        f":white_check_mark: {success_message}", style="green"
                    )
                    return result
                except Exception as e:
                    progress.update(task, advance=1, visible=False)
                    progress.stop()
                    console.print(f":x: {error_message}: {str(e)}", style="red")
                    raise e

        return wrapper

    return decorator
