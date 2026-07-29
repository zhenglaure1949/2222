FROM python:3.11-slim
WORKDIR /analysis
COPY requirements_runtime.txt .
RUN pip install --no-cache-dir -r requirements_runtime.txt
COPY . .
CMD ["python", "scripts/06_validate_outputs_v9.py"]
