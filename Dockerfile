FROM python:3.7-alpine

RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP betrain.app
ENV FLASK_RUN_HOST 0.0.0.0

CMD ["flask", "run"]
