Add `CustomMockMixin` internal class, inheriting from `UnpropagatingMockMixin`, but also allowing to use `spec_set` as
class variable, as it will automatically pass it into `__init__` of the mock class.
