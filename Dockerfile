FROM python:3.10-alpine
WORKDIR /NanoNotABot
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir -m a=rwx /NanoNotABot/config
RUN mkdir -m a=rwx /NanoNotABot/data
COPY NanoNotABot .
CMD ["python", "./main.py"]
