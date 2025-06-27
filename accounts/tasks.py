from core.celery import app


@app.task
def send_otp_to_phone_tasks(otp):
    print(f'Your OTP is: {otp}')
