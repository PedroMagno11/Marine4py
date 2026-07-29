from typing import Any, Callable, Dict, Hashable, Iterable, Optional

"""
FragmentAssembler: remonta payloads que chegam fragmentados em várias
sentenças (padrão comum quando o wire format tem um limite de tamanho
por sentença menor que a mensagem lógica, como no caso do NMEA-0183 e seus
82 caracteres máximos, mas não só dele).

Assim como FramingStrategy e ChecksumStrategy, está classe não assume
nomes de atributo específicos de nenhum dialeto: o chamador injeta,
via callables, como extrair de uma sentenca o total de fragmentos, o
indice do fragmento atual, a chave que agrupa fragmentos da mesma
mensagem, e o payload de cada pedaço. Isso e o que permite o AIS e 
qualquer dialeto proprietario futuro que também fragmente mensagens 
reaproveitarem a mesma lógica de remontagem, cada um só configurando 
os extratores certos.
"""

class FragmentAssembler:
    def __init__(
        self,
        total_count: Callable[[Any], int],
        fragment_index: Callable[[Any], int],
        payload: Callable[[Any], str],
        group_key: Callable[[Any], Hashable],
        combine: Callable[[Iterable[str]], str] = "".join,
    ):
        """
        total_count:    sentenca -> quantos fragmentos a mensagem tem no total
        fragment_index: sentenca -> qual e o indice (1-based) desta sentenca
        payload:        sentenca -> o pedaco de payload que esta sentenca carrega
        group_key:      sentenca -> chave que identifica "todos esses fragmentos
                         pertencem a mesma mensagem" (ex: canal + seq_id no AIS)
        combine:        como juntar os pedacos, na ordem certa, quando completos
                         (default: concatenacao simples de strings)
        """
        self._total_count = total_count
        self._fragment_index = fragment_index
        self._payload = payload
        self._group_key = group_key
        self._combine = combine
        self._pending: Dict[Hashable, Dict[int, str]] = {}

    def feed(self, sentence) -> Optional[str]:
        """
        Recebe uma sentenca ja parseada. Retorna o payload completo
        quando todos os fragmentos da mensagem tiverem chegado, ou
        None se ainda faltam fragmentos.
        """
        total = self._total_count(sentence)
        if total == 1:
            return self._payload(sentence)

        key = self._group_key(sentence)
        parts = self._pending.setdefault(key, {})
        parts[self._fragment_index(sentence)] = self._payload(sentence)

        if len(parts) < total:
            return None  # ainda faltam fragmentos dessa mensagem

        result = self._combine(parts[i] for i in range(1, total + 1))
        del self._pending[key]  # mensagem completa -- libera o estado
        return result

    def pending_count(self) -> int:
        """Quantas mensagens estao com fragmentos incompletos aguardando."""
        return len(self._pending)

    def reset(self) -> None:
        """Descarta todos os fragmentos pendentes (ex: ao reconectar a uma fonte)."""
        self._pending.clear()
