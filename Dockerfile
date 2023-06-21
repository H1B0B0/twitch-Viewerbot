FROM python:3.9
WORKDIR /twitch_bot
COPY . /twitch_bot
RUN pip install --no-cache-dir -r src/requirements.txt
RUN if [ "$(uname)" = "Linux" ]; then \
        apt-get update && apt-get install -y python3-tk; \
    fi
ENV DISPLAY=:0
CMD ["python", "src/main.py"]