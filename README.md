FastKafka
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

<b>Effortless Kafka integration for your web services</b>

------------------------------------------------------------------------

![PyPI](https://img.shields.io/pypi/v/fastkafka.png) ![PyPI -
Downloads](https://img.shields.io/pypi/dm/fastkafka.png) ![PyPI - Python
Version](https://img.shields.io/pypi/pyversions/fastkafka.png)

![GitHub Workflow
Status](https://img.shields.io/github/actions/workflow/status/airtai/fastkafka/test.yaml)
![CodeQL](https://github.com/airtai/fastkafka//actions/workflows/codeql.yml/badge.svg)
![Dependency
Review](https://github.com/airtai/fastkafka//actions/workflows/dependency-review.yml/badge.svg)

![GitHub](https://img.shields.io/github/license/airtai/fastkafka.png)

------------------------------------------------------------------------

[FastKafka](https://fastkafka.airt.ai/) is a powerful and easy-to-use
Python library for building asynchronous services that interact with
Kafka topics. Built on top of [Pydantic](https://docs.pydantic.dev/),
[AIOKafka](https://github.com/aio-libs/aiokafka) and
[AsyncAPI](https://www.asyncapi.com/), FastKafka simplifies the process
of writing producers and consumers for Kafka topics, handling all the
parsing, networking, task scheduling and data generation automatically.
With FastKafka, you can quickly prototype and develop high-performance
Kafka-based services with minimal code, making it an ideal choice for
developers looking to streamline their workflow and accelerate their
projects.

------------------------------------------------------------------------

#### ⭐ Stay in touch

Please show your support and stay in touch by giving our [GitHub
repository](https://github.com/airtai/fastkafka/) a star! Your support
helps us to stay in touch with you and encourages us to continue
developing and improving the library. Thank you for your support!

![Activity](https://repobeats.axiom.co/api/embed/21f36049093d5eb8e5fdad18c3c5d8df5428ca30.svg "Repobeats analytics image")

## Install

FastKafka works on macOS, Linux, and most Unix-style operating systems.
You can install it with `pip` as usual:

``` sh
pip install fastkafka
```

## Tutorial

You can start an interactive tutorial in Google Colab by clicking the
button below:

<a href="https://colab.research.google.com/github/airtai/fastkafka/blob/main/nbs/guides/Guide_00_FastKafka_Demo.ipynb" target=”_blank”>
<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab">
</a>

## Writing server code

Here is an example python script using FastKafka that takes data from a
Kafka topic, makes a prediction using a predictive model, and outputs
the prediction to another Kafka topic.

### Preparing the demo model

First we will prepare our model using the Iris dataset so that we can
demonstrate the preditions using FastKafka. The following call downloads
the dataset and trains the model.

``` python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)
model = LogisticRegression(random_state=0, max_iter=500).fit(X, y)
x = X[[0, 55, -1]]
print(x)
print(model.predict(x))
```

    [[5.1 3.5 1.4 0.2]
     [5.7 2.8 4.5 1.3]
     [5.9 3.  5.1 1.8]]
    [0 1 2]

### Messages

FastKafka uses [Pydantic](https://docs.pydantic.dev/) to parse input
JSON-encoded data into Python objects, making it easy to work with
structured data in your Kafka-based applications. Pydantic’s
[`BaseModel`](https://docs.pydantic.dev/usage/models/) class allows you
to define messages using a declarative syntax, making it easy to specify
the fields and types of your messages.

This example defines two message classes for use in a FastKafka
application:

- The `IrisInputData` class is used to represent input data for a
  predictive model. It has four fields of type
  [`NonNegativeFloat`](https://docs.pydantic.dev/usage/types/#constrained-types),
  which is a subclass of float that only allows non-negative floating
  point values.

- The `IrisPrediction` class is used to represent the output of the
  predictive model. It has a single field `species` of type string
  representing the predicted species.

These message classes will be used to parse and validate incoming data
in Kafka consumers and producers.

``` python
from pydantic import BaseModel, NonNegativeFloat, Field


class IrisInputData(BaseModel):
    sepal_length: NonNegativeFloat = Field(
        ..., example=0.5, description="Sepal length in cm"
    )
    sepal_width: NonNegativeFloat = Field(
        ..., example=0.5, description="Sepal width in cm"
    )
    petal_length: NonNegativeFloat = Field(
        ..., example=0.5, description="Petal length in cm"
    )
    petal_width: NonNegativeFloat = Field(
        ..., example=0.5, description="Petal width in cm"
    )


class IrisPrediction(BaseModel):
    species: str = Field(..., example="setosa", description="Predicted species")
```

### Application

This example shows how to initialize a FastKafka application.

It starts by defining a dictionary called `kafka_brokers`, which
contains two entries: `"localhost"` and `"production"`, specifying local
development and production Kafka brokers. Each entry specifies the URL,
port, and other details of a Kafka broker. This dictionary is used for
generating the documentation only and it is not being checked by the
actual server.

Next, an object of the
[`FastKafka`](https://airtai.github.io/fastkafka/0.2.2/api/fastkafka/FastKafka/#fastkafka.FastKafka)
class is initialized with the minimum set of arguments:

- `kafka_brokers`: a dictionary used for generation of documentation

- `bootstrap_servers`: a `host[:port]` string or list of `host[:port]`
  strings that a consumer or a producer should contact to bootstrap
  initial cluster metadata

``` python
from fastkafka import FastKafka

kafka_brokers = {
    "localhost": {
        "url": "localhost",
        "description": "local development kafka broker",
        "port": 9092,
    },
    "production": {
        "url": "kafka.airt.ai",
        "description": "production kafka broker",
        "port": 9092,
        "protocol": "kafka-secure",
        "security": {"type": "plain"},
    },
}

kafka_app = FastKafka(
    title="Iris predictions",
    kafka_brokers=kafka_brokers,
    bootstrap_servers="localhost:9092",
)
```

### Function decorators

FastKafka provides convenient function decorators `@kafka_app.consumes`
and `@kafka_app.produces` to allow you to delegate the actual process of

- consuming and producing data to Kafka, and

- decoding and encoding JSON encode messages

from user defined functions to the framework. The FastKafka framework
delegates these jobs to AIOKafka and Pydantic libraries.

These decorators make it easy to specify the processing logic for your
Kafka consumers and producers, allowing you to focus on the core
business logic of your application without worrying about the underlying
Kafka integration.

This following example shows how to use the `@kafka_app.consumes` and
`@kafka_app.produces` decorators in a FastKafka application:

- The `@kafka_app.consumes` decorator is applied to the `on_input_data`
  function, which specifies that this function should be called whenever
  a message is received on the “input_data” Kafka topic. The
  `on_input_data` function takes a single argument which is expected to
  be an instance of the `IrisInputData` message class. Specifying the
  type of the single argument is instructing the Pydantic to use
  `IrisInputData.parse_raw()` on the consumed message before passing it
  to the user defined function `on_input_data`.

- The `@produces` decorator is applied to the `to_predictions` function,
  which specifies that this function should produce a message to the
  “predictions” Kafka topic whenever it is called. The `to_predictions`
  function takes a single integer argument `species_class` representing
  one of three possible strign values predicted by the mdoel. It creates
  a new `IrisPrediction` message using this value and then returns it.
  The framework will call the `IrisPrediction.json().encode("utf-8")`
  function on the returned value and produce it to the specified topic.

``` python
@kafka_app.consumes(topic="input_data", auto_offset_reset="latest")
async def on_input_data(msg: IrisInputData):
    global model
    species_class = model.predict(
        [[msg.sepal_length, msg.sepal_width, msg.petal_length, msg.petal_width]]
    )[0]

    to_predictions(species_class)


@kafka_app.produces(topic="predictions")
def to_predictions(species_class: int) -> IrisPrediction:
    iris_species = ["setosa", "versicolor", "virginica"]

    prediction = IrisPrediction(species=iris_species[species_class])
    return prediction
```

## Testing the service

The service can be tested using the
[`Tester`](https://airtai.github.io/fastkafka/0.2.2/api/fastkafka/testing/Tester/#fastkafka.testing.Tester)
instances which internally starts Kafka broker and zookeeper.

Before running tests, we have to install Java runtime and Apache Kafka
locally. To simplify the process, we provide the following convenience
command:

``` sh
fastkafka testing install_deps
```

    [INFO] fastkafka._components.helpers: Installing Java...
    [INFO] fastkafka._components.helpers:  - installing jdk...
    [INFO] fastkafka._components.helpers:  - jdk path: /home/davor/.jdk/jdk-11.0.18+10
    [INFO] fastkafka._components.helpers: Java installed.
    [INFO] fastkafka._components.helpers: Installing Kafka...
    832969it [00:06, 121052.85it/s]                                                 
    [INFO] fastkafka._components.helpers: Kafka installed in /home/davor/.local/kafka_2.13-3.3.2.

``` python
from fastkafka.testing import Tester

msg = IrisInputData(
    sepal_length=0.1,
    sepal_width=0.2,
    petal_length=0.3,
    petal_width=0.4,
)

# Start Tester app and create local Kafka broker for testing
async with Tester(kafka_app) as tester:
    # Send IrisInputData message to input_data topic
    await tester.to_input_data(msg)

    # Assert that the kafka_app responded with IrisPrediction in predictions topic
    await tester.awaited_mocks.on_predictions.assert_awaited_with(
        IrisPrediction(species="setosa"), timeout=2
    )
```

    [INFO] fastkafka._components.helpers: Java is already installed.
    [INFO] fastkafka._components.helpers: But not exported to PATH, exporting...
    [INFO] fastkafka._components.helpers: Kafka is installed.
    [INFO] fastkafka._components.helpers: But not exported to PATH, exporting...
    [INFO] fastkafka._testing.local_broker: Starting zookeeper...
    [INFO] fastkafka._testing.local_broker: Starting kafka...
    [INFO] fastkafka._testing.local_broker: Local Kafka broker up and running on 127.0.0.1:9092
    [INFO] fastkafka._application.app: _create_producer() : created producer using the config: '{'bootstrap_servers': '127.0.0.1:9092'}'
    [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.start(): Entering...
    [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Starting...
    [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Starting send_stream
    [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.start(): Finished.
    [INFO] fastkafka._application.app: _create_producer() : created producer using the config: '{'bootstrap_servers': '127.0.0.1:9092'}'
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() starting...
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer created using the following parameters: {'bootstrap_servers': '127.0.0.1:9092', 'auto_offset_reset': 'latest', 'max_poll_records': 100}
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer started.
    [INFO] aiokafka.consumer.subscription_state: Updating subscribed topics to: frozenset({'input_data'})
    [INFO] aiokafka.consumer.consumer: Subscribed to topic(s): {'input_data'}
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer subscribed.
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() starting...
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer created using the following parameters: {'bootstrap_servers': '127.0.0.1:9092', 'auto_offset_reset': 'earliest', 'max_poll_records': 100}
    [INFO] aiokafka.consumer.group_coordinator: Metadata for topic has changed from {} to {'input_data': 1}. 
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer started.
    [INFO] aiokafka.consumer.subscription_state: Updating subscribed topics to: frozenset({'predictions'})
    [INFO] aiokafka.consumer.consumer: Subscribed to topic(s): {'predictions'}
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer subscribed.
    [INFO] aiokafka.consumer.group_coordinator: Metadata for topic has changed from {} to {'predictions': 1}. 
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer stopped.
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() finished.
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer stopped.
    [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() finished.
    [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Entering...
    [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Exiting send_stream
    [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Finished.
    [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Stoping producer...
    [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Finished
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Terminating the process 1383...
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Process 1383 terminated.
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Terminating the process 1003...
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Process 1003 terminated.

### Recap

We have created a Iris classification model and encapulated it into our
fastkafka application. The app will consume the IrisInputData from the
`input_data` topic and produce the predictions to `predictions` topic.

To test the app we have:

1.  Created the app

2.  Started our Tester class which mirrors the developed app topics for
    testing purpuoses

3.  Sent IrisInputData message to `input_data` topic

4.  Asserted and checked that the developed iris classification service
    has reacted to IrisInputData message

## Running the service

The service can be started using builtin faskafka run CLI command.
Before we can do that, we will concatenate the code snippets from above
and save them in a file `"application.py"`

``` python
# content of the "application.py" file

from pydantic import BaseModel, NonNegativeFloat, Field

class IrisInputData(BaseModel):
    sepal_length: NonNegativeFloat = Field(
        ..., example=0.5, description="Sepal length in cm"
    )
    sepal_width: NonNegativeFloat = Field(
        ..., example=0.5, description="Sepal width in cm"
    )
    petal_length: NonNegativeFloat = Field(
        ..., example=0.5, description="Petal length in cm"
    )
    petal_width: NonNegativeFloat = Field(
        ..., example=0.5, description="Petal width in cm"
    )


class IrisPrediction(BaseModel):
    species: str = Field(..., example="setosa", description="Predicted species")
    
from fastkafka import FastKafka

kafka_brokers = {
    "localhost": {
        "url": "localhost",
        "description": "local development kafka broker",
        "port": 9092,
    },
    "production": {
        "url": "kafka.airt.ai",
        "description": "production kafka broker",
        "port": 9092,
        "protocol": "kafka-secure",
        "security": {"type": "plain"},
    },
}

kafka_app = FastKafka(
    title="Iris predictions",
    kafka_brokers=kafka_brokers,
    bootstrap_servers="localhost:9092",
)

iris_species = ["setosa", "versicolor", "virginica"]

@kafka_app.consumes(topic="input_data", auto_offset_reset="latest")
async def on_input_data(msg: IrisInputData):
    global model
    species_class = model.predict([
          [msg.sepal_length, msg.sepal_width, msg.petal_length, msg.petal_width]
        ])[0]

    to_predictions(species_class)


@kafka_app.produces(topic="predictions")
def to_predictions(species_class: int) -> IrisPrediction:
    prediction = IrisPrediction(species=iris_species[species_class])
    return prediction
```

To run the service, you will need a running Kafka broker on localhost as
specified by the `bootstrap_servers="localhost:9092"` parameter above.
We can start the Kafka broker locally using the
[`LocalKafkaBroker`](https://airtai.github.io/fastkafka/0.2.2/api/fastkafka/testing/LocalKafkaBroker/#fastkafka.testing.LocalKafkaBroker).
Notice that the same happens automatically in the
[`Tester`](https://airtai.github.io/fastkafka/0.2.2/api/fastkafka/testing/Tester/#fastkafka.testing.Tester)
as shown above.

    [INFO] fastkafka._testing.local_broker: LocalKafkaBroker.start(): entering...
    [WARNING] fastkafka._testing.local_broker: LocalKafkaBroker.start(): (<_UnixSelectorEventLoop running=True closed=False debug=False>) is already running!
    [WARNING] fastkafka._testing.local_broker: LocalKafkaBroker.start(): calling nest_asyncio.apply()
    [INFO] fastkafka._components.helpers: Java is already installed.
    [INFO] fastkafka._components.helpers: Kafka is installed.
    [INFO] fastkafka._testing.local_broker: Starting zookeeper...
    [INFO] fastkafka._testing.local_broker: Starting kafka...
    [INFO] fastkafka._testing.local_broker: Local Kafka broker up and running on 127.0.0.1:9092
    [INFO] fastkafka._testing.local_broker: <class 'fastkafka.testing.LocalKafkaBroker'>.start(): returning 127.0.0.1:9092
    [INFO] fastkafka._testing.local_broker: LocalKafkaBroker.start(): exited.

    '127.0.0.1:9092'

Then, we start the FastKafka service by running the following command in
the folder where the `application.py` file is located:

``` sh
fastkafka run --num-workers=2 application:kafka_app
```

    [3715]: [INFO] fastkafka._application.app: _create_producer() : created producer using the config: '{'bootstrap_servers': 'localhost:9092'}'
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.start(): Entering...
    [3713]: [INFO] fastkafka._application.app: _create_producer() : created producer using the config: '{'bootstrap_servers': 'localhost:9092'}'
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.start(): Entering...
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Starting...
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Starting send_stream
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.start(): Finished.
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Starting...
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Starting send_stream
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.start(): Finished.
    [3713]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() starting...
    [3713]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer created using the following parameters: {'bootstrap_servers': 'localhost:9092', 'auto_offset_reset': 'latest', 'max_poll_records': 100}
    [3715]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() starting...
    [3715]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer created using the following parameters: {'bootstrap_servers': 'localhost:9092', 'auto_offset_reset': 'latest', 'max_poll_records': 100}
    [3713]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer started.
    [3715]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer started.
    [3713]: [INFO] aiokafka.consumer.subscription_state: Updating subscribed topics to: frozenset({'input_data'})
    [3715]: [INFO] aiokafka.consumer.subscription_state: Updating subscribed topics to: frozenset({'input_data'})
    [3713]: [INFO] aiokafka.consumer.consumer: Subscribed to topic(s): {'input_data'}
    [3713]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer subscribed.
    [3715]: [INFO] aiokafka.consumer.consumer: Subscribed to topic(s): {'input_data'}
    [3715]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer subscribed.
    [3715]: [ERROR] aiokafka.cluster: Topic input_data not found in cluster metadata
    [3715]: [INFO] aiokafka.consumer.group_coordinator: Metadata for topic has changed from {} to {'input_data': 0}. 
    [3713]: [WARNING] aiokafka.cluster: Topic input_data is not available during auto-create initialization
    [3713]: [INFO] aiokafka.consumer.group_coordinator: Metadata for topic has changed from {} to {'input_data': 0}. 
    [3715]: [ERROR] aiokafka: Unable connect to node with id 0: [Errno 111] Connect call failed ('192.168.176.2', 9092)
    [3713]: [ERROR] aiokafka: Unable connect to node with id 0: [Errno 111] Connect call failed ('192.168.176.2', 9092)
    [3713]: [ERROR] aiokafka: Unable to update metadata from [0]
    [3715]: [ERROR] aiokafka: Unable to update metadata from [0]
    ^C
    Starting process cleanup, this may take a few seconds...
    [INFO] fastkafka._server: terminate_asyncio_process(): Terminating the process 3713...
    [INFO] fastkafka._server: terminate_asyncio_process(): Terminating the process 3715...
    [3715]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer stopped.
    [3715]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() finished.
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Entering...
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Exiting send_stream
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Finished.
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Stoping producer...
    [3715]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Finished
    [3713]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop(): Consumer stopped.
    [3713]: [INFO] fastkafka._components.aiokafka_consumer_loop: aiokafka_consumer_loop() finished.
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Entering...
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Exiting send_stream
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: _aiokafka_producer_manager(): Finished.
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Stoping producer...
    [3713]: [INFO] fastkafka._components.aiokafka_producer_manager: AIOKafkaProducerManager.stop(): Finished

You need to interupt running of the cell above by selecting
`Runtime->Interupt execution` on the toolbar above.

Finally, we can stop the local Kafka Broker:

    [INFO] fastkafka._testing.local_broker: LocalKafkaBroker.stop(): entering...
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Terminating the process 3102...
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Process 3102 was already terminated.
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Terminating the process 2723...
    [INFO] fastkafka._components._subprocess: terminate_asyncio_process(): Process 2723 was already terminated.
    [INFO] fastkafka._testing.local_broker: LocalKafkaBroker.stop(): exited.

## Documentation

The kafka app comes with builtin documentation generation using
[AsyncApi HTML generator](https://www.asyncapi.com/tools/generator).

AsyncApi requires Node.js to be installed and we provide the following
convenience command line for it:

``` sh
fastkafka docs install_deps
```

    [INFO] fastkafka._components.asyncapi: AsyncAPI generator installed

To generate the documentation programatically you just need to call the
folloving command:

``` sh
fastkafka docs generate application:kafka_app
```

    [INFO] fastkafka._components.asyncapi: New async specifications generated at: '/work/fastkafka/nbs/asyncapi/spec/asyncapi.yml'
    [INFO] fastkafka._components.asyncapi: Async docs generated at 'asyncapi/docs'
    [INFO] fastkafka._components.asyncapi: Output of '$ npx -y -p @asyncapi/generator ag asyncapi/spec/asyncapi.yml @asyncapi/html-template -o asyncapi/docs --force-write'

    Done! ✨
    Check out your shiny new generated files at /work/fastkafka/nbs/asyncapi/docs.

. This will generate the *asyncapi* folder in relative path where all
your documentation will be saved. You can check out the content of it
with:

``` sh
ls -l asyncapi
```

    total 8
    drwxrwxr-x 4 davor davor 4096 Mar  3 20:07 docs
    drwxrwxr-x 2 davor davor 4096 Jan 25 09:30 spec

In docs folder you will find the servable static html file of your
documentation. This can also be served using our `fastkafka docs serve`
CLI command (more on that in our guides).

In spec folder you will find a asyncapi.yml file containing the async
API specification of your application.

We can locally preview the generated documentation by running the
following command:

``` sh
fastkafka docs serve application:kafka_app
```

    [INFO] fastkafka._components.asyncapi: New async specifications generated at: '/work/fastkafka/nbs/asyncapi/spec/asyncapi.yml'
    [INFO] fastkafka._components.asyncapi: Async docs generated at 'asyncapi/docs'
    [INFO] fastkafka._components.asyncapi: Output of '$ npx -y -p @asyncapi/generator ag asyncapi/spec/asyncapi.yml @asyncapi/html-template -o asyncapi/docs --force-write'

    Done! ✨
    Check out your shiny new generated files at /work/fastkafka/nbs/asyncapi/docs.


    Serving documentation on http://127.0.0.1:8000
    ^C
    Interupting serving of documentation and cleaning up...

From the parameters passed to the application constructor, we get the
documentation bellow:

``` python
from fastkafka import FastKafka

kafka_brokers = {
    "localhost": {
        "url": "localhost",
        "description": "local development kafka broker",
        "port": 9092,
    },
    "production": {
        "url": "kafka.airt.ai",
        "description": "production kafka broker",
        "port": 9092,
        "protocol": "kafka-secure",
        "security": {"type": "plain"},
    },
}

kafka_app = FastKafka(
    title="Iris predictions",
    kafka_brokers=kafka_brokers,
    bootstrap_servers="localhost:9092",
)
```

![Kafka_servers](https://raw.githubusercontent.com/airtai/fastkafka/main/nbs/images/screenshot-kafka-servers.png)

The following documentation snippet are for the consumer as specified in
the code above:

![Kafka_consumer](https://raw.githubusercontent.com/airtai/fastkafka/main/nbs/images/screenshot-kafka-consumer.png)

The following documentation snippet are for the producer as specified in
the code above:

![Kafka_producer](https://raw.githubusercontent.com/airtai/fastkafka/main/nbs/images/screenshot-kafka-producer.png)

Finally, all messages as defined as subclasses of *BaseModel* are
documented as well:

![Kafka\_![Kafka_servers](https://raw.githubusercontent.com/airtai/fastkafka/main/nbs/images/screenshot-kafka-messages.png)](https://raw.githubusercontent.com/airtai/fastkafka/main/nbs/images/screenshot-kafka-messages.png)

## License

FastKafka is licensed under the Apache License 2.0

A permissive license whose main conditions require preservation of
copyright and license notices. Contributors provide an express grant of
patent rights. Licensed works, modifications, and larger works may be
distributed under different terms and without source code.

The full text of the license can be found
[here](https://raw.githubusercontent.com/airtai/fastkafka/main/LICENSE).
