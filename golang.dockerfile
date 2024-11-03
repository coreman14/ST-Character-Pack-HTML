# syntax=docker/dockerfile:1

FROM golang:1.23.2

# Set destination for COPY
WORKDIR /app

# Download Go modules
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code. Note the slash at the end, as explained in
# https://docs.docker.com/reference/dockerfile/#copy
COPY *.go /app
COPY /serverConfig /app/serverConfig
COPY /views /app/views
COPY /htmlAssets /app/htmlAssets

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o /docker-gs-ping

# Optional:
# To bind to a TCP port, runtime parameters must be supplied to the docker 
EXPOSE 80

# Run
CMD ["/docker-gs-ping"]