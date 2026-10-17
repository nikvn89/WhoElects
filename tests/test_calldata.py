"""Measure canonical positional GenLayer calldata, not character counts."""
import pytest
from genlayer_py.abi import calldata
from genlayer_py.contracts.utils import make_calldata_object

@pytest.mark.parametrize('method,args',[
    ('open_option',['0x'+'a'*40,'é'*12,'é'*28,'a'*40,'b'*40]),
    ('open_option',['0x'+'a'*40,'C','é'*60,'a'*19,'b'*20]),
    ('elect',['f'*64,'é'*20]),
    ('object_to_election',['f'*64,'é'*30]),
    ('withdraw_option',['f'*64]),
    ('get_option',['f'*64]),
])
def test_serialized_calls_fit_255_bytes(method,args):
    raw=calldata.encode(make_calldata_object(method=method,args=args))
    assert len(raw)<=255,(method,len(raw))
