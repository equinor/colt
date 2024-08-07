FROM python:3.13.0a6-alpine3.18

RUN pip install --no-cache rdflib PyGithub

WORKDIR /usr/src

COPY src .

ENTRYPOINT [ "python", "/usr/src/main.py" ]