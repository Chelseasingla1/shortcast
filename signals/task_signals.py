import logging
from celery.signals import task_success, task_failure, task_received, task_retry
from task_singleton import TaskInfoSingleton


def handle_task_info(task_id):
    """
    Helper function to handle the common logic for logging task info.

    Args:
        task_id: The ID of the task.
    """
    task_info_singleton = TaskInfoSingleton()
    task_name = task_info_singleton.get_task_info(task_id)

    if not task_name:
        logging.warning(f"No task name found for task ID: {task_id}")
        return None

    return task_name


@task_received.connect
def task_received_handler(sender=None, task_id=None, **kwargs):
    """
    Signal handler for when a task is received.
    """
    request = kwargs.get("request")
    if not request:
        logging.warning("No request object found in the task_received signal.")
        return

    task_id = request.id  # Extract task ID from the request object
    logging.info(f"Task received with ID: {task_id}")

    task_name = handle_task_info(task_id)
    if task_name:
        logging.info(f"Task {task_id} of type '{task_name}' received.")
    else:
        logging.warning(f"Task {task_id} of unknown type received.")


@task_success.connect
def task_success_handler(sender=None, result=None, task_id=None, **kwargs):
    """
    Signal handler for task success events.
    """
    task_id = getattr(sender, 'request', {}).get('id', None)
    if not task_id:
        logging.warning("No task ID found in task_success signal.")
        return

    logging.info(f"Task {task_id} succeeded with result: {result}")

    task_name = handle_task_info(task_id)
    if task_name:
        logging.info(f"Task {task_id} of type '{task_name}' succeeded.")
    else:
        logging.warning(f"Task {task_id} of unknown type succeeded.")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """
    Signal handler for task failure events.
    """
    task_name = handle_task_info(task_id)
    if task_name:
        logging.error(f"Task {task_id} of type '{task_name}' failed with exception: {exception}")
    else:
        logging.warning(f"Task {task_id} of unknown type failed with exception: {exception}")


@task_retry.connect
def task_retry_handler(sender=None, exception=None, task_id=None, **kwargs):
    """
    Signal handler for task retry events.
    """
    task_name = handle_task_info(task_id)
    if task_name:
        logging.info(f"Task {task_id} of type '{task_name}' is being retried due to exception: {exception}")
    else:
        logging.warning(f"Task {task_id} of unknown type is being retried due to exception: {exception}")
