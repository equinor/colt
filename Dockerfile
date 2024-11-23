FROM python:3.14.0a2-alpine3.20

RUN pip install --no-cache rdflib PyGithub

WORKDIR /usr/src

COPY src .

ENTRYPOINT [ "python", "/usr/src/main.py" ]