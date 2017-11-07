FROM python:3.6

WORKDIR /usr/src/app
ENV FLASK_APP app.py

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m flask load
CMD ["python", "-m", "flask", "run"]