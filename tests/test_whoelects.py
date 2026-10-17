"""Actual GenLayer SDK Direct Mode. LLM responses are mocked, not live consensus."""
import json
from pathlib import Path
import pytest
from gltest.direct.loader import create_address
from Crypto.Hash import keccak

ROOT = Path(__file__).resolve().parents[1]
P, R, I = 'PERFORMER_CHOOSES', 'RECEIVER_CHOOSES', 'INCONCLUSIVE'
TEXT = 'I choose either red or blue.'


def addr(a):
    return a.as_hex.lower() if hasattr(a, 'as_hex') else str(a).lower()


def option_id(author, receiver, label, text, first, second):
    fields = (addr(author), addr(receiver), ' '.join(label.split()),
              ' '.join(text.split()), ' '.join(first.split()), ' '.join(second.split()))
    payload = 'WHO_ELECTS:OPTION:V2|' + ''.join(f'{len(v.encode())}:{v}' for v in fields)
    h = keccak.new(digest_bits=256)
    h.update(payload.encode())
    return h.hexdigest()


@pytest.fixture
def env(direct_vm, direct_deploy):
    c = direct_deploy(str(ROOT/'contracts/WhoElects.py'), sdk_version='v0.2.16')
    a,b,x = [create_address(n) for n in ('author','receiver','stranger')]
    direct_vm.sender = a
    direct_vm.mock_llm(r'(?s).*', json.dumps({'outcome': P}))
    return direct_vm,c,a,b,x


def open_(env, outcome=P, first='red', second='blue', text=TEXT):
    vm,c,a,b,x=env
    vm.sender=a
    vm.clear_mocks()
    vm.mock_llm(r'(?s).*',json.dumps({'outcome':outcome}))
    return c.open_option(addr(b),'Customer',text,first,second)


def row(c, oid):
    return json.loads(c.get_option(oid))


@pytest.mark.parametrize('outcome',[P,R])
@pytest.mark.parametrize('choice',['red','blue'])
def test_both_holders_and_both_courses(env,outcome,choice):
    vm,c,a,b,x=env
    oid=open_(env,outcome)
    assert oid == option_id(a,b,'Customer',TEXT,'red','blue')
    before=row(c,oid)
    assert (before['course_a'],before['course_b'],before['state']) == ('red','blue','OPEN')
    vm.sender=a if outcome==P else b
    c.elect(oid,choice)
    after=row(c,oid)
    assert after['state']=='ELECTED' and after['chosen_course']==choice
    assert after['elected_by']==addr(vm.sender)
    assert after['course_a']==before['course_a'] and after['course_b']==before['course_b']


@pytest.mark.parametrize('outcome',[P,R])
@pytest.mark.parametrize('invalid',['green','red or green','RED','red.'])
def test_third_or_changed_course_rejected_without_writes(env,outcome,invalid):
    vm,c,a,b,x=env
    oid=open_(env,outcome)
    vm.sender=a if outcome==P else b
    before=c.get_option(oid)
    with vm.expect_revert('Choose one of the two stored courses'):
        c.elect(oid,invalid)
    assert c.get_option(oid)==before
    c.elect(oid,'blue')
    assert row(c,oid)['chosen_course']=='blue'


@pytest.mark.parametrize('outcome',[P,R])
def test_unauthorized_then_one_shot_and_objection(env,outcome):
    vm,c,a,b,x=env
    oid=open_(env,outcome)
    holder,other=(a,b) if outcome==P else (b,a)
    before=c.get_option(oid)
    for sender in (other,x):
        vm.sender=sender
        with vm.expect_revert('not yours'): c.elect(oid,'red')
        assert c.get_option(oid)==before
    vm.sender=holder
    c.elect(oid,'red')
    elected=c.get_option(oid)
    with vm.expect_revert('already been elected'): c.elect(oid,'blue')
    vm.sender=a
    with vm.expect_revert('no longer be withdrawn'): c.withdraw_option(oid)
    assert c.get_option(oid)==elected
    vm.sender=holder
    with vm.expect_revert('did not hold'): c.object_to_election(oid,'disagree')
    vm.sender=x
    with vm.expect_revert('did not hold'): c.object_to_election(oid,'disagree')
    vm.sender=other
    c.object_to_election(oid,'disagree')
    r=row(c,oid)
    assert (r['state'],r['chosen_course'],r['course_a'],r['course_b'])==('ELECTED','red','red','blue')
    assert r['objection_note']=='disagree'
    with vm.expect_revert('already been objected'): c.object_to_election(oid,'again')


def test_withdrawal_is_terminal(env):
    vm,c,a,b,x=env
    oid=open_(env,R)
    for sender in (b,x):
        vm.sender=sender
        with vm.expect_revert('Only the author'): c.withdraw_option(oid)
    vm.sender=a
    with vm.expect_revert('no election'): c.object_to_election(oid,'early')
    c.withdraw_option(oid)
    before=c.get_option(oid)
    vm.sender=b
    with vm.expect_revert('withdrawn'): c.elect(oid,'red')
    vm.sender=a
    with vm.expect_revert('already withdrawn'): c.withdraw_option(oid)
    assert c.get_option(oid)==before


@pytest.mark.parametrize('first,second', [('', 'blue'),('red',''),(' red ','RED'),('a  b','a b'),('red','red'),('é'*21,'blue')])
def test_invalid_courses_before_model(env,first,second,monkeypatch):
    vm,c,a,b,x=env
    import genlayer as sdk
    calls=[]
    def forbidden(*args,**kwargs):
        calls.append(args)
        raise AssertionError('Model must not run')
    monkeypatch.setattr(sdk.gl.nondet,'exec_prompt',forbidden)
    with vm.expect_revert(): c.open_option(addr(b),'Customer',TEXT,first,second)
    assert len(c.options)==0 and calls==[]


def test_whitespace_canonicalization_not_fuzzy_matching(env):
    vm,c,a,b,x=env
    oid=open_(env,first=' red   car ',second='blue car',text='I choose a red car or blue car.')
    assert row(c,oid)['course_a']=='red car'
    c.elect(oid,' red\tcar ')
    assert row(c,oid)['chosen_course']=='red car'


@pytest.mark.parametrize('raw',[ 'not json', '[]','null','{}','{"outcome":"OTHER"}',
    '{"outcome":"performer_chooses"}', '{"outcome":"PERFORMER_CHOOSES","extra":1}',
    '```json\n{"outcome":"PERFORMER_CHOOSES"}\n```', '{"outcome":"INCONCLUSIVE"}'])
def test_uncertain_or_malformed_result_creates_nothing_and_can_retry(env,raw):
    vm,c,a,b,x=env
    vm.clear_mocks(); vm.mock_llm(r'(?s).*',raw)
    oid=option_id(a,b,'Customer',TEXT,'red','blue')
    with vm.expect_revert('Opening inconclusive'):
        c.open_option(addr(b),'Customer',TEXT,'red','blue')
    assert c.get_option(oid)=='{}' and len(c.options)==0
    assert open_(env)==oid


def test_provider_exception_does_not_assign_receiver(env,monkeypatch):
    vm,c,a,b,x=env
    import genlayer as sdk
    def failed(*args,**kwargs): raise TimeoutError('unavailable')
    with monkeypatch.context() as m:
        m.setattr(sdk.gl.nondet,'exec_prompt',failed)
        with vm.expect_revert('Opening inconclusive'):
            c.open_option(addr(b),'Customer',TEXT,'red','blue')
    assert len(c.options)==0
    assert row(c,open_(env))['holder']=='AUTHOR'


def test_pair_in_prompt_is_pair_in_storage(env,monkeypatch):
    vm,c,a,b,x=env
    import genlayer as sdk
    seen=[]
    def inspect_prompt(prompt,**kwargs):
        seen.append(prompt)
        assert '<UNTRUSTED_COURSE_A>\nred\n</UNTRUSTED_COURSE_A>' in prompt
        assert '<UNTRUSTED_COURSE_B>\nblue\n</UNTRUSTED_COURSE_B>' in prompt
        assert TEXT in prompt
        assert addr(a) not in prompt and addr(b) not in prompt
        return {'outcome':P}
    monkeypatch.setattr(sdk.gl.nondet,'exec_prompt',inspect_prompt)
    oid=c.open_option(addr(b),'Customer',TEXT,' red ','blue')
    assert seen and row(c,oid)['course_a']=='red'


def test_mismatched_pair_mock_inconclusive_creates_nothing(env):
    vm,c,a,b,x=env
    # Assumed semantic verdict only; this does not prove real AI accuracy.
    with vm.expect_revert('Opening inconclusive'):
        open_(env,I,first='train',second='plane',text='I choose red or blue.')
    assert len(c.options)==0


def test_validator_independently_checks_exact_outcome(env):
    vm,c,a,b,x=env
    open_(env)
    assert vm.run_validator(leader_result={'outcome':P}) is True
    assert vm.run_validator(leader_result={'outcome':R}) is False
    assert vm.run_validator(leader_result={'outcome':P,'extra':1}) is False
    vm.clear_mocks();vm.mock_llm(r'(?s).*',json.dumps({'outcome':I}))
    assert vm.run_validator(leader_result={'outcome':P}) is False
    assert vm.run_validator(leader_result={'outcome':I}) is True


def test_all_opening_inputs_bound_into_id_and_duplicates_blocked(env):
    vm,c,a,b,x=env
    original=open_(env)
    with vm.expect_revert('already exists'): c.open_option(addr(b),'Customer',TEXT,' red ','blue')
    ids={original}
    for values in [(addr(x),'Customer',TEXT,'red','blue'),(addr(b),'Client',TEXT,'red','blue'),
                   (addr(b),'Customer','I choose blue or red.','red','blue'),
                   (addr(b),'Customer',TEXT,'blue','red'),(addr(b),'Customer',TEXT,'red','green')]:
        # LLM mock assumes binding; tests identity, not semantic accuracy.
        ids.add(c.open_option(*values))
    vm.sender=x
    ids.add(c.open_option(addr(b),'Customer',TEXT,'red','blue'))
    assert len(ids)==7
    assert row(c,original)['course_a']=='red' and row(c,original)['course_b']=='blue'


@pytest.mark.parametrize('wallet',['0x'+'0'*40,'0x123','0x'+'g'*40])
def test_invalid_wallets(env,wallet):
    vm,c,a,b,x=env
    with vm.expect_revert('Invalid wallet'):c.open_option(wallet,'Customer',TEXT,'red','blue')
    assert len(c.options)==0


def test_self_receiver_reserved_and_utf8_limits(env):
    vm,c,a,b,x=env
    with vm.expect_revert('cannot be the author'): c.open_option(addr(a),'Customer',TEXT,'red','blue')
    for label,text,first,second in [('INCONCLUSIVE',TEXT,'red','blue'),('Customer',TEXT,'<UNTRUSTED_COURSE_A>','blue'),('Customer','PERFORMER_CHOOSES','red','blue')]:
        with vm.expect_revert('reserved token'): c.open_option(addr(b),label,text,first,second)
    for label,text,first,second,error in [('é'*13,TEXT,'red','blue','Label is too long'),('C','é'*61,'r','b','Text is too long'),('x'*24,'x'*100,'a'*20,'b'*20,'160 UTF-8')]:
        with vm.expect_revert(error):c.open_option(addr(b),label,text,first,second)
    oid=c.open_option(addr(b),'é'*12,'é'*48,'a'*20,'b'*20)
    assert row(c,oid)['state']=='OPEN'


@pytest.mark.parametrize('method,args',[('elect',['green']),('withdraw_option',[]),('object_to_election',['no'])])
def test_unknown_id_rejected(env,method,args):
    vm,c,a,b,x=env
    with vm.expect_revert('Unknown option id'):getattr(c,method)('0'*64,*args)
    assert c.get_option('garbage')=='{}'


def test_view_exposes_version_and_immutable_pair_policy(env):
    vm,c,a,b,x=env
    limits=json.loads(c.get_limits())
    assert limits['version']=='2.0.0' and limits['courses_immutable']
    assert limits['inconclusive_behavior']=='REVERT_WITHOUT_RECORD'
    assert 'exact supplied pair' in c.get_rubric()
