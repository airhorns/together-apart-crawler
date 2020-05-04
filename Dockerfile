FROM python:3.7.7-buster
RUN pip install pipenv
ENV PIPENV_VENV_IN_PROJECT=true

RUN mkdir /app
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy

COPY . /app
CMD ["pipenv", "run", "python", "src/scrape.py"]