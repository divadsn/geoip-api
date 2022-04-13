FROM python:3.10-alpine
LABEL maintainer="David Sn <divad.nnamtdeis@gmail.com>"

# Install dependencies
RUN apk add --no-cache --update curl git

# Copy app files
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . ./
ENTRYPOINT ["uvicorn", "geoip_api:app"]

CMD ["--host", "0.0.0.0", "--port", "8069", "--proxy-headers"]
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl --silent --fail http://localhost:8069/healthcheck || exit 1
