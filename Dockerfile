FROM python:3.9
COPY . .
WORKDIR /ecrops
RUN pip install .

WORKDIR /EcropsWofostExampleConsole

CMD [ "python", "main.py" ]