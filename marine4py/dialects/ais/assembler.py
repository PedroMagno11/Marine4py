from marine4py.core.assembler import FragmentAssembler
from marine4py.dialects.ais.sentences import VDM, VDO


class AisAssembler(FragmentAssembler):
    def __init__(self):
        super().__init__(
            total_count=lambda s: s.frag_count,
            fragment_index=lambda s: s.frag_number,
            payload=lambda s: s.payload,
            group_key=lambda s: (s.channel, s.seq_id),
        )

    def feed(self, sentence):
        if not isinstance(sentence, (VDM, VDO)):
            raise TypeError(
                f"AisAssembler.feed espera uma sentenca VDM/VDO, recebeu {type(sentence).__name__}"
            )
        return super().feed(sentence)
