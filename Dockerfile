FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERES=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . . 
RUN mkdir -p/app/instance
EXPOSE 5000
CMD ["python","app.py"]
