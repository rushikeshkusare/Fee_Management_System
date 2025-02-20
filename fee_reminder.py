from apscheduler.schedulers.blocking import BlockingScheduler
from app import send_email, fetch_fees

def send_scheduled_reminders():
    due_fees = fetch_fees()
    due_fees = due_fees[due_fees['amount_paid'] < due_fees['amount_due']]

    for _, row in due_fees.iterrows():
        send_email(row['email'], row['student_name'], row['amount_due'], row['due_date'])

# Set up scheduler
scheduler = BlockingScheduler()
scheduler.add_job(send_scheduled_reminders, 'cron', day=5, hour=9, minute=0)  # Every 5th
scheduler.add_job(send_scheduled_reminders, 'cron', day=20, hour=9, minute=0)  # Every 20th

print("Reminder scheduler started...")
scheduler.start()
