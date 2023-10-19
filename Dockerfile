FROM python:3.9 AS builder
 
WORKDIR /app
COPY . /app
 
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
RUN pip install -r requirements.txt

# Stage 2
FROM python:3.9 AS runner
 
WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY . /app
 
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m nltk.downloader punkt
 
EXPOSE 8000
CMD [ "uvicorn", "--host", "0.0.0.0", "main:app" , "--port", "8000"]

