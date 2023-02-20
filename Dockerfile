FROM python:3.10

RUN pip install --upgrade pip

COPY . /proj
WORKDIR /proj
RUN pip install .

CMD [ "uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8080" ]
