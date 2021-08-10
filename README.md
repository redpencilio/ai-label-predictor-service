# ai-label-predictor-service

A docker container for labeling text with an AI model trained with
the [ai-label-trainer-service](https://github.com/redpencilio/ai-label-trainer-service).

## Getting started

```yml
services:
  label-predictor:
    image: redpencil/ai-label-predictor
    environment:
      LOG_LEVEL: "debug"
      MODE: "production"
    links:
      - db:database
    volumes:
      - ./share:/share
```

It is important that the `model.py` file is exactly the same file as used in
the [ai-label-trainer-service](https://github.com/redpencilio/ai-label-trainer-service)!

## Reference

### Environment variables

- `LOG_LEVEL` takes the same options as defined in the
  Python [logging](https://docs.python.org/3/library/logging.html#logging-levels) module.


- `MU_SPARQL_ENDPOINT` is used to configure the SPARQL query endpoint.

    - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should
      be linked to the microservice container as `database`.


- `MU_SPARQL_UPDATEPOINT` is used to configure the SPARQL update endpoint.

    - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should
      be linked to the microservice container as `database`.


- `MU_APPLICATION_GRAPH` specifies the graph in the triple store the microservice will work in.

    - By default this is set to `http://mu.semte.ch/application`. The graph name can be used in the service
      via `settings.graph`.


- `MU_SPARQL_TIMEOUT` is used to configure the timeout (in seconds) for SPARQL queries.

### Endpoints

#### `GET /label`: make a prediction

Arguments:

- model: id of the file that contains the model trained to make the predictions with
  the [ai-label-trainer-service](https://github.com/redpencilio/ai-label-trainer-service). The file id can be found in
  the result of the job that was created to start training.
- text: text for which a label should be predicted

## Improvements

For now, the trained model is loaded every time a request is made to make a prediction. The advantage of this is that
multiple trained models can be used with this service. To improve performance, the id of the model could be passed as an
environment variable and preloaded on startup.
