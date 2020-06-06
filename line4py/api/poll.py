from typing import List, Dict, Callable

from line4py.service.TalkService import TalkService
from line4py.service.TalkService.ttypes import Operation, OpType

_MAX_COUNT = 50


class LongPollingClient(TalkService.Client):
    revision: int = 0

    def __init__(self, iprot):
        super().__init__(iprot)

        self.operations = {}

    def set_last_revision(self):
        self.revision = self.getLastOpRevision()

    def fetch(self) -> List[Operation]:
        ops = self.fetchOperations(self.revision, _MAX_COUNT)

        for op in ops:
            if op.type == OpType.END_OF_OPERATION:
                continue
            elif op.revision < self.revision:
                continue

            self.revision = op.revision

        return ops

    def handle(
            self, ops: List[Operation]
    ) -> Dict[Callable[[Operation], None], Operation]:
        return {
            self.operations[op.type]: op
            for op in ops
            if op.type in self.operations
        }

    def add_operation(self, op_type: OpType, func: Callable[[Operation], None]):
        self.operations[op_type] = func
