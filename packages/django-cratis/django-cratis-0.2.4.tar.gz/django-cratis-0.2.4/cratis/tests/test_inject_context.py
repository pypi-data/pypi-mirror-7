
import inject

from cratis.utils.tests import inject_services

def test_inject_services():
    class Boo():
        pass

    class Baz():
        pass

    def configure(binder):
        binder.bind(Boo, Baz())

    with inject_services(configure):
        instance = inject.instance(Boo)
        assert isinstance(instance, Baz)
