FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir /app
WORKDIR /app

COPY ./sca /app/sca
RUN pip install --no-cache-dir -r /app/sca/requirements.txt
COPY ./sca_cli.py /app/

CMD ["python", "sca_cli.py"]