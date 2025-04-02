from uuid import UUID, uuid4

from doxer.domain.ports import IdGeneratorProtocol


class UuidGenerator(IdGeneratorProtocol):
    def generate_id(self) -> UUID:
        return uuid4()