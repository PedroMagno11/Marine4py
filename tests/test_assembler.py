from dataclasses import dataclass
from typing import Optional

from marine4py.core.assembler import FragmentAssembler


@dataclass
class FakeFragment:
    """
    Simula uma sentenca de um dialeto proprietario fictício que também
    fragmenta mensagens grandes -- com nomes de campo totalmente
    diferentes dos usados pelo AIS (aqui: total/index/group/chunk),
    para provar que o FragmentAssembler nao depende de nomenclatura
    nenhuma. So existe para estes testes.
    """
    total: int
    index: int
    group: str
    chunk: str


def make_assembler():
    return FragmentAssembler(
        total_count=lambda f: f.total,
        fragment_index=lambda f: f.index,
        payload=lambda f: f.chunk,
        group_key=lambda f: f.group,
    )


def test_single_fragment_returns_immediately():
    assembler = make_assembler()
    frag = FakeFragment(total=1, index=1, group="A", chunk="payload-completo")
    assert assembler.feed(frag) == "payload-completo"
    assert assembler.pending_count() == 0


def test_multi_fragment_waits_until_complete():
    assembler = make_assembler()
    assert assembler.feed(FakeFragment(total=2, index=1, group="A", chunk="parte1-")) is None
    assert assembler.pending_count() == 1
    result = assembler.feed(FakeFragment(total=2, index=2, group="A", chunk="parte2"))
    assert result == "parte1-parte2"
    assert assembler.pending_count() == 0


def test_fragments_arrive_out_of_order():
    # index 2 chega antes do index 1 -- o assembler deve remontar na
    # ordem correta mesmo assim, nao na ordem de chegada.
    assembler = make_assembler()
    assembler.feed(FakeFragment(total=2, index=2, group="A", chunk="-fim"))
    result = assembler.feed(FakeFragment(total=2, index=1, group="A", chunk="inicio"))
    assert result == "inicio-fim"


def test_interleaved_groups_do_not_mix():
    assembler = make_assembler()
    assembler.feed(FakeFragment(total=2, index=1, group="navio-A", chunk="A1-"))
    assembler.feed(FakeFragment(total=2, index=1, group="navio-B", chunk="B1-"))
    assert assembler.pending_count() == 2

    result_a = assembler.feed(FakeFragment(total=2, index=2, group="navio-A", chunk="A2"))
    assert result_a == "A1-A2"
    assert assembler.pending_count() == 1  # navio-B ainda pendente

    result_b = assembler.feed(FakeFragment(total=2, index=2, group="navio-B", chunk="B2"))
    assert result_b == "B1-B2"
    assert assembler.pending_count() == 0


def test_custom_combine_function():
    # combine customizado: junta com separador em vez de concatenar cru
    assembler = FragmentAssembler(
        total_count=lambda f: f.total,
        fragment_index=lambda f: f.index,
        payload=lambda f: f.chunk,
        group_key=lambda f: f.group,
        combine=lambda parts: "|".join(parts),
    )
    assembler.feed(FakeFragment(total=2, index=1, group="A", chunk="um"))
    result = assembler.feed(FakeFragment(total=2, index=2, group="A", chunk="dois"))
    assert result == "um|dois"


def test_reset_clears_pending_state():
    assembler = make_assembler()
    assembler.feed(FakeFragment(total=3, index=1, group="A", chunk="x"))
    assert assembler.pending_count() == 1
    assembler.reset()
    assert assembler.pending_count() == 0
