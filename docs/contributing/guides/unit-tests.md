# Testing the library

???+ abstract

    This article explains how to write unit-tests with the pytest framework, showcasing
    the basics of testing, good practices, etc. Additionally, it also explains our testing
    file structure, toolings we use for testing and other guidelines.

    This guide is fairly long as it covers the basics of testing alongside various examples
    to get even the complete beginners comfortable and familiar with how python tests work.
    If you're already familiar with some of these concepts, you may benefit from skipping
    certain chapters.

Since there are many people that rely on this library working properly, and we don't want to accidentally introduce
some changes which would cause it to break, we're using unit-tests that validate the individual components in our
code-base work properly.

_**NOTE:** This is a practical guide to quickly get you started with writing unit-tests, not a full introduction to what
unit-tests are. That means it will only cover the basics and general concepts. If you're looking for a full
introduction, you can take a look at the [Additional Resources](#additional-resources) section at the bottom._

## Tools

We are using the following modules and packages for our unit tests:

We are using the following modules and packages for our unit tests:

- [pytest](https://docs.pytest.org/en/6.2.x/)
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/index.html)
- [coverage.py](https://coverage.readthedocs.io/en/stable/) (as a part of pytest-cov)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) (standard library)

We decided on using `pytest` instead of the `unittest` module from standard library since it's much more beginner
friendly and it's generally easier to use.

## Running tests

When running the tests, you should always be in an activated virtual environment (or use `poetry run` to run commands
for the tests from within the environment).

To make things simpler, we made a few shortcuts/aliases using taskipy:

- `poetry run task test-nocov` will run all unit-tests using `pytest`.
- `poetry run task test` will run `pytest` with `pytest-cov`, collecting code coverage information
- `poetry run task test tests/test_foobar.py` will run specific test
- `poetry run task retest` will rerun only previously failed tests

When actively developing, you'll most likely only be working on some portion of the code-base, and as the result, you
won't need to run the entire test suite, instead you can only run tests for a specific file with

```sh
poetry run task test /path/to/test.py
```

When you are done and are preparing to commit and push your code, it's a good idea to run the entire test suite as a
sanity check that you haven't accidentally introduced some unexpected bugs:

```sh
poetry run task test
```

## Writing tests

Since consistency is an important consideration for collaborative projects, we have written some guidelines on writing
tests for the project. In addition to these guidelines, it's a good idea to look at the existing code base for examples.

### File and directory structure

To organize our test suite, we have chosen to mirror the directory structure of [`mcproto`](/mcproto/) in
[`tests/mcproto`](/tests/mcproto) directory. This makes it easy to find the relevant tests by providing a natural
grouping of files. More general testing files, such as [`helpers.py`](/tests/helpers.py) are located directly in the
`tests` directory.

All files containing tests should have a filename starting with `test_` to make sure `pytest` will discover them.
This prefix is typically followed by the name of the file the tests are written for.

## Writing independent tests

When writing unit tests, it's important to make sure that each test that you write runs independently from all of
the other tests. This both means that the code you write for one test shouldn't influence the result of another test
and that if one tests fails, the other tests should still run.

Each of test should only ever cover a single subproblem, and if something else needs testing, it should be in another
independent test. This then prevents tests for X from failing because of Y, instead Y should be tested in another test.
In other words, don't write tests that check "everything", rather, write multiple smaller tests.

However, independent tests often require similar preparation steps. Since you'll be splitting these tests, to avoid
repetition, `pytest` provides [fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) that can be executed before and
after each test is run. In addition to test fixtures, it also provides support for
[parametrization](https://docs.pytest.org/en/6.2.x/example/parametrize.html), which is a way of re-running the same
test function with different values. If there's a failure, pytest will then show us the values that were being used
when this failure occurred, making it a much better solution than just manually using them in the test function.

### Using parametrization to repeat the same tests with different values

```python
import pytest


def add(x: int, y: int) -> int:
    return x + y

@pytest.mark.parametrize(
    ("num1", "num2", "expected_result"),
    [
        (1, 1, 2),
        (1, 0, 1),
        (0, 0, 0),
        (5, -5, 0),
    ]
)
def test_add(num1: int, num2: int, expected_result: int) -> None:
    assert add(num1, num2) == expected_result
```

### Using fixtures to prepare shared setup for multiple tests

```python
import pytest


class User:
    def __init__(self, name: str) -> None:
        self.name = name

@pytest.fixture
def test_user() -> User:
    return User(name="John Doe")


def test_user_name_starts_with_capital(user: User) -> None:
    assert user.name[0].isupper()


def test_user_name_contains_space(user: User) -> None:
    assert " " in user.name
```

Here, both tests get access to the same user instance, created cleanly and consistently before each test. Pytest takes
care of calling the user() fixture and passing its return value into the test function.

Fixtures can be very versatile, as you can even perform patching within them, request other fixtures within fixtures,
etc. You should check out the [pytest documentation on fixtures][pytest-fixtures].

## Mocking

As we are trying to test our "units" of code independently, we want to make sure that we don't rely on objects and data
generated by "external" code (things like database queries, API calls or even our own utility functions). This is
because when relying on external objects, we might end up observing a failure for reasons unrelated to the specific
logic we're trying to validate, e.g. a failure in one of the utility methods of that object, rather than the code we're
actually testing here.

You can think of mocks as "fake" objects, that behave like the real ones, but give us full control over what exactly
they do, allowing us to focus on testing our code, and not the utilities around it (those deserve their own tests, if
internal).

In Python, we use the [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) module (part of python's
standard library) to create these mock objects.

### Basic Example: Mocking a socket

Let’s say you’re testing a `PizzaOrder` class that depends on a delivery service. You don’t want to actually call the
real delivery service in your test - that could cost money (and confuse your local pizzeria).

So instead, you mock it:

```python
from unittest.mock import Mock
from collections.abc import Callable

class DeliveryService:
    def send(self, pizza_type: str, quantity: int) -> str:
        # Imagine this sends a request to an external delivery API.
        raise NotImplementedError("Real delivery not implemented")

class PizzaOrder:
    def __init__(self, delivery_service: DeliveryService):
        self.delivery_service = delivery_service
        self.confirmation = self.delivery_service.send("Margherita", 2)

def test_order_triggers_delivery():
    mock_service = MagicMock()
    mock_service.send.return_value = "Order #42 confirmed"

    order = PizzaOrder(mock_service)

    assert order.confirmation == "Order #42 confirmed"
    mock_service.send.assert_called_once_with("Margherita", 2)
```

We created a mock `delivery_service`, with a fake `send` function, instructed to return a specific value, and then
confirmed that it was called with the right arguments. And the best part? No pizzas were ordered in the making of this
test.

### More interactive example: Different Orders, Different confirmations

Mocks can do much more than just return the same value every time. If you want your mock to behave differently based on
how it’s called - like returning different results for different pizza orders - you can use the `side_effect` argument
instead of `return_value`.

Let’s say we want the delivery service to give us different confirmation messages based on the pizza being ordered. We
can test that with a mock that changes the behavior based on the input using `side_effect`:

```python
def test_dynamic_delivery_confirmations() -> None:
    def fake_send(pizza: str, count: int) -> str:
        if pizza == "Hawaiian":
            return "Sorry, we don't deliver pineapple crimes."
        return f"Confirmed: {count}x {pizza}"

    mock_service = MagicMock()
    mock_service.send.side_effect = fake_send

    order1 = PizzaOrder(mock_service, "Margherita", 2)
    order2 = PizzaOrder(mock_service, "Hawaiian", 1)

    assert order1.confirmation == "Confirmed: 2x Margherita"
    assert order2.confirmation == "Sorry, we don't deliver pineapple crimes."

    assert mock_service.send.call_count == 2
    mock_service.send.assert_any_call("Margherita", 2)
    mock_service.send.assert_any_call("Hawaiian", 1)
```

Now your mock is **dynamic** - it behaves like a miniature fake system, giving you different outputs based on inputs.
This is incredibly useful when testing code that has to respond to multiple conditions.

### Other uses of `side_effect`

We’ve seen how `side_effect` can be used to return different results based on the input, by passing it a callable. But
that’s not the only thing it can do. The `side_effect` parameter is surprisingly versatile and supports several
powerful patterns:

#### Raising Exceptions

You can use `side_effect` to easily simulate errors by assigning it to an exception class or instance. This is useful
when testing how your code handles failure cases, like a delivery service outage.

```python
def test_delivery_failure() -> None:
    mock_service = MagicMock()
    mock_service.send.side_effect = RuntimeError("Delivery system is down")

    with pytest.raises(RuntimeError):
        PizzaOrder(mock_service, "Pepperoni", 1)
```

You could of course also use a full function that would raise internally, but this is a much more convenient way to
achieve it.

#### Sequence of return values (and/or exceptions)

Instead of writing a function, you can also assign `side_effect` a list (or any iterable). On each call, the mock will
return the next value in the sequence, or raise an exception if the next item is one.

This is great when testing retries, fallbacks, or just varied responses:

```python
def test_multiple_calls_with_varied_outcomes() -> None:
    mock_service = MagicMock()
    mock_service.send.side_effect = [
        "Confirmed: 1x Margherita",
        RuntimeError("Out of dough"),
        "Confirmed: 1x Pepperoni",
    ]

    order1 = PizzaOrder(mock_service, "Margherita", 1)
    assert order1.confirmation == "Confirmed: 1x Margherita"

    with pytest.raises(RuntimeError):
        PizzaOrder(mock_service, "Hawaiian", 1)

    order3 = PizzaOrder(mock_service, "Pepperoni", 1)
    assert order3.confirmation == "Confirmed: 1x Pepperoni"
```

!!! info

    The mock will raise `StopIteration` if you call it more times than there are items, so keep the list long enough
    for your test case.

### Using `spec_set`

By default, mocks are _very_ permissive; You can access any attribute or call any method on them and it’ll “just work”.
That’s great for flexibility, but not so great for catching typos or invalid method calls.

As an example, this code would work:

```python
from unittest.mock import Mock

my_mock = Mock()
x = my_mock.made_up_method().even_more_fake().foobar() # x will be just another mock object
```

To tighten this up, use the `spec_set` argument. It tells the mock to only allow access to attributes/methods that exist
on a given object or type.

Let's see an example of how this could be useful:

```python
def greet(name: str) -> str:
    return name.capatilize() + ", welcome!"  # Oops!


def test_foo():
    mock_str = Mock(spec_set=str)
    greet(mock_str)  # AttributeError: Mock object has no attribute 'capitilize'
```

Boom! The typo gets caught immediately. Setting `spec_set=str` means the mock will only allow attributes that actually
exist on a real `str` object.

!!! tip

    You can also use `spec` (instead of `spec_set`) , which will restrict which attributes and methods you can access
    (based on the original object - like with `spec_set`), but still allows you to set new ones dynamically. E.g.
    allows `mock.foobar = 1` and later use of `mock.foobar`. For stricter validation, stick with `spec_set`.

There is one important thing to keep in mind though. `spec_set` only applies to the first level. For example, if you
call `mock.removesuffix(";").removeprefx(";")`, only the first call (`removesuffix`) is validated. The return value is
a regular unrestricted Mock, so the second typo slips through.

!!! tip "Multi-level spec-set mocks"

    If you need a stricter multi-level mocks, you can manually configure return values, for example like so:

    ```python
    inner = Mock(spec_set=inner_object_spec)
    outer = Mock(spec_set=outer_object_spec, some_method=Mock(return_value=inner))

    outer.some_method  # this will now give you the `inner` mock
    ```

    But honestly, this usually isn't worth the effort, unless the return value is something you're specifically testing.
    Mocks should help you target specific behavior, not recreate every detail of the real world, after all, that's what
    we're actually trying to avoid.

### Mock types

So far, we've only used the `Mock` class, which is the most common and flexible type of mock object. But depending on
what you're testing, you might run into situations where `Mock` is not enough.

Python’s `unittest.mock` module gives you a few specialized variants:

#### `MagicMock`

`MagicMock` is just like `Mock`, but it also supports Python’s magic methods (like `__len__`, `__getitem__`,
`__enter__`, etc.). Use this if you're mocking an object that behaves like a container, context manager, or something
else with special behavior.

```python
from unittest.mock import MagicMock

mock_list = MagicMock()
len(mock_list)  # works, returns another mock

mock_list.__len__.return_value = 3  # also works (regular Mocks don't let you set __len__)
assert len(mock_list) == 3
```

#### `AsyncMock`

`AsyncMock` is designed for mocking asynchronous code, like async functions, coroutines, and `await`-able objects. If
you mock an async function with a regular `Mock`, it won't actually be awaitable and your test might break (or worse,
pass silently without actually testing anything).

This comes up all the time when dealing with I/O: databases, APIs, background tasks, etc.

```python
import pytest
from unittest.mock import AsyncMock

# Here's our async function that relies on some async data fetch
async def praise_user(user_id: int, fetch_user: Callable[[int], Awaitable[User]]):
    user = await fetch_user(user_id)
    return f"{user['name']} is doing great!"

async def test_praise_user() -> None:
    # Set up a fake async function that returns a predictable value
    mock_fetch_user = AsyncMock(return_value={"id": 42, "name": "Jake"})

    # Inject it just like you would in real code
    message = await praise_user(42, fetch_user=mock_fetch_user)

    assert message == "Jake is doing great!"
    mock_fetch_user.assert_awaited_once_with(42)
```

### When NOT to use Mocks

Mocks are great for isolating code and avoiding unwanted side effects, but don’t reach for them by default. If a
function calls a simple internal utility that’s tightly coupled to its behavior, it's often fine to let it run as-is.

Mocking that utility might make your test harder to read, or even force you to replicate its behavior in the mock -
which defeats the point. In cases like that, it's usually best to treat the utility as part of the logic under test,
especially when the utility is already well-tested on its own, making using the real thing often safer and more reliable
than a rough imitation.

**Rule of thumb:** If mocking something makes your test more vague, or you'd have to "rebuild" its logic just to fake
it, skip the mock and use the real implementation. But if the utility has unwanted side effects (like API calls or disk
writes), mocking is the right call.

### Designing a more involved example (socket mocking)

Now that we know a fair bit about mocks, let's take a look at something closer to what you'll see in our codebase.

What if we wanted to ensure that our connection can properly read data that were sent to us through a socket?

```python
import socket
from unittest.mock import Mock

from mcproto.connection import TCPSyncConnection


def test_connection_reads_correct_data():
    mock_socket = Mock(spec_set=socket.socket)
    mock_socket.recv.return_value = bytearray("data", "utf-8")
    conn = TCPSyncConnection(mock_socket)

    received = conn.read(4)  # 4 bytes, for 4 characters in the word "data"
    assert received == bytearray("data", "utf-8")
    mock_socket.recv.assert_called_once_with(4)
```

Cool! But in real tests, we'll often want to make use of something a bit more complicated, as right now, our `recv`
mock method will just naively return 4 byte long data no matter what the passed length attribute was. In the earlier
example, this isn't a huge problem, but the issue begins to surface when we try to read a more complex custom format,
like a varint for example, which can involve more reads with differing lengths that together just form a single
number, encoded in a specific way.

We could do this with `side_effect` and specify a list of byte values that would be returned from each read, however,
we don't want to rely on the specific read sizes, for us, those are an implementation detail, and we don't want our
tests to test implementation, rather, we just want to test the external behavior.

It would also be nice to make this a bit more general, so that we can reuse a mock that would behave in this way
across multiple tests for various connection methods.

Doing all this is a bit more complex, but it's still doable, let's see it:

```python
from unittest.mock import Mock

from mcproto.connection import TCPSyncConnection


class ReadFunctionMock(Mock):
    def __init__(self, *a, combined_data: bytearray, **kw):
        super().__init__(*a, **kw)
        self.combined_data = combined_data

    def __call__(self, length: int) -> bytearray:
        """Override mock's `__call__` to make it return part of our `combined_data` bytearray.

        This allows us to make the return value always be the next requested part (length) of
        the `combined_data`. It would be difficult to replicate this with regular mocks,
        because some functions can end up making multiple read calls, and each time the result
        needs to be different (the next part).
        """
        self.return_value = self.combined_data[:length]
        del self.combined_data[:length]

        # Call base Mock's __call__, this will return the above set return_value
        # while also registering the call
        return super().__call__(length)

class MockSocket(Mock):
    def __init__(self, *args, read_data: bytearray, **kwargs) -> None:
        super().__init__(*args, spec_set=socket.socket, **kwargs)
        self._recv = ReadFunctionMock(combined_data=read_data)

    def recv(self, length: int) -> bytearray:
        return self._recv(length)


def test_connection_partial_read():
    mock_socket = MockSocket(read_data=bytearray("data", "utf-8"))
    conn = TCPSyncConnection(mock_socket)

    data1 = conn.read(2)
    assert data1 == bytearray("da", "utf-8")
    data2 = conn.read(2)
    assert data2 == bytearray("ta", "utf-8")

def test_connection_empty_read_fails():
    mock_socket = MockSocket(read_data=bytearray())
    conn = TCPSyncConnection(mock_socket)

    with pytest.raises(IOError, match="Server did not respond with any information."):
        conn.read(1)

def test_connection_read_varint():
    varint_bytes = [128, 128, 1]  # bytes forming number 16384 in varint encoding
    mock_socket = MockSocket(read_data=bytearray(varint_bytes))
    conn = TCPSyncConnection(mock_socket)

    result = conn.read_varint()  # will make a bunch of reads

    assert result == 16384
```

## Patching

Even though mocking is a great way to let us use fake objects acting as real ones, without patching, we can only use
mocks as arguments. However that greatly limits us in what we can test, or places restrictions on how we have to
implement our internal behavior, just to make it testable. In practice, some functions may be calling/referencing the
external resources that we'd like to mock directly inside of them, without being overridable through arguments.

Cases like these are when patching comes into the picture. Basically, patching is just about (usually temporarily)
replacing some built-in / external code object, by a mock, or some other object that we can control from the tests.

A good example would be for example the `open` function for reading/writing files. We likely don't want any actual files
to be written during our testing, however we might need to test a function that writes some files internally, and
perhaps check that the content written matches some pattern, ensuring that it works properly.

While there is some built-in support for patching in the [unittest.mock
library](https://docs.python.org/3/library/unittest.mock.html#the-patchers), we generally use `pytest`'s
[monkeypatching](https://docs.pytest.org/en/7.1.x/how-to/monkeypatch.html) as it can act as a fixture and integrates
well with the rest of our test codebase, which is written with pytest in mind.

### Faking the time

Let’s start with something small, but oddly satisfying: pretending that the current time is whatever we want. Maybe you
have a function that behaves differently on weekends, or logs the current date in a specific format.

```python
from datetime import datetime

def get_greeting():
    now = datetime.now()
    if now.hour < 12:
        return "Good morning"
    return "Good afternoon"
```

Here’s how we can fake time using `monkeypatch` and control `datetime.now()`:

```python
import pytest
from datetime import datetime

from yourmodule import get_greeting

def test_morning_greeting(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_datetime = Mock(spec_set=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 9, 0)

    # Patch datetime *where it is used* — e.g., "yourmodule.datetime"
    monkeypatch.setattr("yourmodule.datetime", mock_datetime)

    assert get_greeting() == "Good morning"

def test_afternoon_greeting(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_datetime = Mock(spec_set=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 15, 0)

    # Patch datetime *where it is used* — e.g., "yourmodule.datetime"
    monkeypatch.setattr("yourmodule.datetime", mock_datetime)

    assert get_greeting() == "Good afternoon"
```

### Patching attribute on an imported class

Let’s say your code needs to fetch some mysterious prophecy from a remote server. But you're a responsible developer and
don’t want your tests waiting on actual prophecies.

```python
import httpx

async def fetch_prophecy():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://fake.api/prophecy")
        return response.json()["message"]
```

We’ll use `AsyncMock` to fake both the async `.get()` call and the context manager behavior of `AsyncClient`:

```python
import pytest
from unittest.mock import AsyncMock, Mock

from yourmodule import fetch_prophecy

async def test_fetch_prophecy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Fake response object with json() returning our pretend prophecy
    fake_response = Mock()
    fake_response.json.return_value = {"message": "The bug shall return at dusk."}

    # AsyncMock for the client, get() is awaited
    fake_client = AsyncMock()
    fake_client.get.return_value = fake_response

    # Make sure AsyncClient works as an async context manager
    fake_client.__aenter__.return_value = fake_client

    # Patch the constructor of AsyncClient to return our fake client
    monkeypatch.setattr("yourmodule.httpx.AsyncClient", lambda: fake_client)

    result = await fetch_prophecy()

    assert result == "The bug shall return at dusk."
    fake_client.get.assert_awaited_once_with("https://fake.api/prophecy")
```

## Some considerations

Finally, there are some considerations to make when writing tests, both for writing tests in general and for writing
tests for our project in particular.

### Test coverage is a starting point

Having test coverage is a good starting point for unit testing: If a part of your code was not covered by a test, we
know that we have not tested it properly. The reverse is unfortunately not true: Even if the code we are testing has
100% branch coverage, it does not mean it's fully tested or guaranteed to work.

One problem is that 100% branch coverage may be misleading if we haven't tested our code against all the realistic
input it may get in production. For instance, take a look at the following `format_join_time` function and the test
we've written for it:

```python
# Source file:
from datetime import datetime

def format_join_time(name: str, time: datetime | None = None) -> str:
    str_time = time.strfptime("%d-%m-%Y") if time else "unknown"
    return f"User {name!r} has joined, time: {str_time}"

# Test file:
from source_file import format_join_time

def test_format_join_time():
    res = format_join_time("ItsDrike", None)
    assert res == "User 'ItsDrike' has joined, time: unknown"
```

If you were to run this test, the function pass the test, and the branch coverage would show 100% coverage for
this function. Can you spot the bug the test suite did not catch?

The problem here is that we have only tested our function with a time that was `None`. That means that
`time.strptime("%d-%m-%Y)` was never executed during our test, leading to us missing the spelling mistake in
`strfptime` (it should be `strftime`).

The reason this wasn't reported is because ternary conditions are on a single line, and even if the first branch of the
if wasn't executed, since it was syntactically touched and the `if time else` ternary got evaluated, coverage report
shows the line as executed. (See [this github issue](https://github.com/nedbat/coveragepy/issues/509) for more info, if
you're interested)

Adding another test would not increase the test coverage we have, but it does ensure that we'll notice that this
function can fail with realistic data

```python
def test_format_join_time_with_non_none_time():
    res = format_join_time("ItsDrike", datetime(2022, 12, 31)
    assert "User 'ItsDrike' has joined" in res
```

Leading to the test catching our bug:

```
collected 2 items

tests/test_foo.py::test_format_join_time_with_non_none_time FAILED                                [ 50%]
tests/test_foo.py::test_format_join_time PASSED                                                   [100%]

=============================================== FAILURES ===============================================
_______________________________ test_format_join_time_with_non_none_time _______________________________

    def test_format_join_time_with_non_none_time():
>       res = format_join_time("ItsDrike", datetime(2022, 12, 31))

tests/test_foo.py:11:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'ItsDrike', time = datetime.datetime(2022, 12, 31, 0, 0)

    def format_join_time(name: str, time: Optional[datetime] = None) -> str:
>       str_time = time.strfptime("%d-%m-%Y") if time else "unknown"
E       AttributeError: 'datetime.datetime' object has no attribute 'strfptime'. Did you mean: 'strftime'?

foo.py:5: AttributeError
======================================= short test summary info ========================================
FAILED tests/test_foo.py::test_format_join_time_with_non_none_time - AttributeError: 'datetime.datetime'
 object has no attribute 'strfptime'. Did you mean: 'strftime'?
=================-============= 1 failed, 1 passed, 0 warnings in 0.02s ================================
```

What's more, even though the second test was able to spot the second mistake, even if it wasn't there, that test is
still not good enough. That's because the assertion in it is not actually checking for whether the time format is what
we'd expect. Perhaps we expect the function to show a format like `time: 04/15/25`, but this function gives us
`15-04-2025`, which is not at all what we want, and yet, coverage-wise, every line of the tested code was ran. We just
didn't check thoroughly enough.

Another way coverage can be misleading is with cases like division, where you can get a `ZeroDivisionError`, which won't
be counted as one of the branch options when measuring coverage, so you might miss it.

All in all, it's not only important to consider if all statements or branches were touched at least once with a test,
but also if they are extensively tested in all situations that may happen in production.

### Unit Testing vs Integration Testing

Another restriction of unit testing is that it tests, well, in units. Even if we can guarantee that the units work as
they should independently, we have no guarantee that they will actually work well together. Even more, while the mocking
described above gives us a lot of flexibility in factoring out external code, we are working under the implicit
assumption that we fully understand those external parts and utilize it correctly. What if our mocked `fetch_prophecy`
function returns a response with the `message` field, but the actual API was changed to now use a `prophecy` field in a
recent update? It could mean our tests are passing, but the code it's testing still doesn't work in production.

## Additional resources

- [Quick guide on using mocks in official python docs](https://docs.python.org/3/library/unittest.mock.html#quick-guide)
- [Official pytest docs](https://docs.pytest.org/en/stable/)
- [Ned Batchelder's PyCon talk: Getting Started Testing](https://www.youtube.com/watch?v=FxSsnHeWQBY)
- [Corey Schafer video about unittest](https://youtu.be/6tNS--WetLI)
- [RealPython tutorial on unittest testing](https://realpython.com/python-testing/)
- [RealPython tutorial on mocking](https://realpython.com/python-mock-library/)

## Footnotes

This document was heavily inspired by [python-discord's tests
README](https://github.com/python-discord/bot/blob/main/tests/README.md)

[pytest-fixtures]: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html
