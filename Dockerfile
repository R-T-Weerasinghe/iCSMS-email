FROM python:3.12.0-slim

WORKDIR /app

# DO NOT CHANGE the order - messes up the cache
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu

COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt

# TO be removed
RUN pip install simplegmail

RUN pip cache purge

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]