# MathMan by Instructure
## Introduction
This is a simple microservice that converts LaTeX formulae to MathML and SVG.
It can either be run locally via `docker-compose`, or on Amazon Lambda.

## Quick start (for Docker)
1. Install docker and docker-compose.
2. Run `cp docker-compose.dev.override.yml docker-compose.override.yml`
3. Run `docker-compose build`.
4. Run `docker-compose run --rm web npm install`.
5. Run `docker-compose up`.

This will launch the microservice, along with a Redis cache. The service
is available at `http://mathman.docker`.

The API interface is `/mml?tex=<tex-string>` or `svg?tex=<tex-string>`.

## Tests
1. Run `docker-compose build` if you haven't already.
2. Run `cp docker-compose.dev.override.yml docker-compose.override.yml`
3. Run `docker-compose run --rm web npm install`.
4. Run `docker-compose run --rm web npm test`.

## Deploy

### Package the code for lambda

1. Run `docker-compose run --rm web npm install`.
2. Run `docker-compose run --rm web ./deploy/package $(git rev-parse
   --short HEAD)`.

The result will be `build/lambda.zip` which can be uploaded to AWS as a
lambda function.
