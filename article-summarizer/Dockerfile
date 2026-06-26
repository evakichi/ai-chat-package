FROM pytorch/pytorch:2.12.1-cuda12.6-cudnn9-runtime

USER root

RUN apt-get update && apt-get -y upgrade && apt-get update && apt-get install -y curl less vim

RUN pip install --break-system-package fastapi uvicorn python-multipart tika transformers[torch]

EXPOSE 8861
