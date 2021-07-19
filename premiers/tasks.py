from celery import shared_task


@shared_task
def tick_tack():
    print("Tick Tack")
