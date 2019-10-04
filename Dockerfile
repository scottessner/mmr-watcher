# Start with latest LTS of Ubuntu
FROM python:3.5.6
MAINTAINER Scott Essner <scott.essner@gmail.com>

RUN groupadd watchergroup -g 1001 && useradd -m -u 1000 -g watchergroup watcher

RUN mkdir -p /opt/watcher
WORKDIR /opt/watcher

RUN mkdir -p /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R watcher:watchergroup .

USER watcher

CMD ["python", "main.py"]