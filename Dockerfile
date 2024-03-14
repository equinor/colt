FROM python:3.9.18-alpine3.18

RUN pip install --no-cache rdflib PyGithub

WORKDIR /usr/src

COPY src .

ENTRYPOINT [ "python", "/usr/src/main.py" ]