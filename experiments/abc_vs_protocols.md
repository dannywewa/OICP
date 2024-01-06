# ABC and Protocols

https://jellis18.github.io/post/2022-01-11-abc-vs-protocol/

In Python, there are two similar, yet different, concepts for defining
something akin to an interface, or a contract describing what methods
and attributes a class will contain. These are ABC and Protocols.

Until the advent of type annotations, ABCs were the way to go if you
wanted to have any kind of validation on class/instance methods or
properties and `isinstance` checks. With type annotations, ABCs
became more relevant as a way to define an "interface" for a given class
hierarchy. With Protocols we can use *structural subtyping* or "Duct
typing" (i.e. the class only has to have the same methods and attributes,
no subclassing necessary).

## What are ABCs

In general there are two use cases for ABCs, as a pure ABC that defines
an "interface" and as a tool for code re-use via the Framework Design
Pattern or through Mixins.

**Pure ABCs (ABC as interface)**

```Python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def walk(self) -> None:
        pass

    @abstractmethod
    def speak(self) -> None:
        pass


class Dog(Animal):
    def walk(self) -> None:
        print('This is a dog walking')

    def speak(self) -> None:
        print('Woof!')
```

**ABCs as a tool for code reuse**

Another, and probably more common, use case for ABCs is for code reuse. Below
is a slightly more realiztic example of a base class for a statiscal or
Machine Learning regression model.

```Python
from abc import ABC, abstractmethod
from typing import List, TypeVar

T = TypeVar('T', bound='Model')

class Model(ABC):
    def __init__(self):
        self._is_fitted = False

    def fit(self: T, data: np.ndarray, target: np.ndarray) -> T:
        fitted_model = self._fit(data, target)
        self._is_fitted = True
        return fitted_model

    def predict(self, data: np.ndarray) -> List[float]:
        if not self._is_fitted:
            raise ValueError(f"{self.__class__.__name__} must be fit before calling predict")
        return self._predict(data)

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    @abstractmethod
    def _fit(self: T, data: np.ndarray, target: np.ndarray) -> T:
        pass

    @abstractmethod
    def _predict(self, data: np.ndarray) -> List[float]:
        pass
```

There are two public methods, `fit` and `predict`. The abstract methods
`_fit` and `_predict` must be defined in subclasses.

Let's implement a super simple model:

```Python
class MeanRegressor(Model):
    def __init__(self):
        super().__init__()
        self._mean = None

    def _fit(self, data: np.ndarray, target: np.ndarray) -> "MeanRegressor":
        self._mean = target.mean()
        return self

    def _predict(self, data: np.ndarray) -> List[float]:
        return list(np.ones(data.shape[0]) * self._mean)
```

## What are Protocols

Protocols were introduced as a way to formally incorporate structural
subtyping (or "duck" typing) into the python type annotation system.

There are two main, but related, use cases for Protocols. First, they can be
used as an interface for classes and functions which can be used downstream
in other classes or functions. Secondly, they can be used to set bounds on
generic types.

**Protocols as interface**

```Python
from typing import Protocol

class Animal(Protocol):
    def walk(self) -> None:
        ...

    def speak(self) -> None:
        ...
```

Ok, let's now implement a Dog
```Python
class Dog:
    def walk(self) -> None:
        print("This is a dog walking")

    def speak(self) -> None:
        print("Woof!")
        
```

One last thing to mention about using Protocols as interface is that it is
possible to make them useable at runtime via an `isinstance` check with the
`runtime_checkable` decorator.

```Python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Animal(Protocol):
    def walk(self) -> None:
        ...

    def speak(self) -> None:
        ...

>>> dog = Dog()
>>> isinstance(dog, Animal)
True
```

## Protocols as Generic Type Bounds

```Python
from typing import TypeVar, Protocol


class SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...

S = TypeVar("S", bound=SupportsLessThan)

def my_max(x: S, y: S) -> S:
    if x < y:
        return y
    return x
```

## So ABC or Protocol?

Yes. You should use both as they are good at different things and both
have should their place in your toolbox. We have already seen above the
main use cases for ABCs and Protocols and how they work. Given those
examples here are some good overall suggestions and observations.

**ABC**

- Belong to their subclasses.
- ABCs are a good mechanism for code reuse, especially for boilerplate
code or logic that will not change for any subclasses. The best
strategy here is to have the ABC do most of the work and have the
children implement the specifics.
- Good for real time validation when *creating* an instance of a child
class.

**Protocol**

- Belong where they are used.
- Good for defining interfaces, especially for 3rd-party libraries when
we don't want to tightly couple our code to a specific 3rd party library.
- Good for specifying flexible generic type bounds.

Ok, so we know that ABCs and Protocols are, we know what they are good at.
So when should we use them? The answer to that is somewhat subjective and
depends on your environment but here are some rules of thumb

- Use ABCs if you want to reuse code. Inheritance is not always the best
method of code reuse but it can be quite useful.
- Use ABCs if you require strict class hierarchy (as in you need to use
method resolution order or you need to check `__subclasses__`) in your
application.
- Use ABCs if you will need several implementations of a class with
several methods.
- Use Protocols for strict type annotations (i.e.only annotate the
methods/attributes you need)
- Use Protocols for generic bounds
- Use Protocols for abstract interfaces for 3rd party libraries
