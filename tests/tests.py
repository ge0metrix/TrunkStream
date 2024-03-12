
from trunkstream.models import *


def test_normal_case():
    call: Call = mock_call()
    assert call.id == 1