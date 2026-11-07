FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV ENABLE_TEST_ROUTES=0
EXPOSE 8000
# One worker on purpose: the demo keeps its data in memory.
CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:8000", "-w", "1", "--threads", "8"]
