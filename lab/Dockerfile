FROM python:3.12-slim
WORKDIR /app
COPY lab/server.py /app/server.py
RUN useradd --uid 10001 --create-home lab && mkdir /data && chown lab:lab /data
USER lab
ENV LAB_DB=/data/lab.sqlite LAB_HOST=0.0.0.0 LAB_PORT=8080
CMD ["python", "/app/server.py"]

