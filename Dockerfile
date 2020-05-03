FROM python:3.7.7-slim-buster
RUN pip install pipenv
RUN mkdir /app
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy
COPY . /app
CMD ["pipenv", "run", "src/scrape.py"]