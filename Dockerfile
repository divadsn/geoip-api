FROM python:3.10-alpine
LABEL maintainer="David Sn <divad.nnamtdeis@gmail.com>"

# Install dependencies
RUN apk add --no-cache --update git

# Copy app files
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . ./
EXPOSE 8069

ENTRYPOINT ["uvicorn", "geoip_api:app"]
CMD ["--host", "0.0.0.0", "--port", "8069", "--proxy-headers"]
