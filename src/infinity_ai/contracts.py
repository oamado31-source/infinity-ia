"""Pure read-only envelope validators; not an EEex bridge implementation."""
from dataclasses import dataclass
from enum import Enum

class Status(str, Enum):
    OBSERVED = 'OBSERVED'
    UNKNOWN = 'UNKNOWN'
    BLOCKED_CAPABILITY = 'BLOCKED_CAPABILITY'

@dataclass(frozen=True)
class Observation:
    campaign_id: str
    branch_id: str
    host_epoch: int
    build_fingerprint: str
    adapter_version: str
    field: str
    status: Status
    value: str | None = None

    def __post_init__(self):
        if not all((self.campaign_id, self.branch_id, self.build_fingerprint,
                    self.adapter_version, self.field)) or self.host_epoch < 0:
            raise ValueError('Incomplete observation identity')
        if self.status is not Status.OBSERVED and self.value is not None:
            raise ValueError('No inferred value for unknown/blocked observation')
        if self.status is Status.OBSERVED and self.value is None:
            raise ValueError('Observed field requires evidence value')

ALLOWED_FIELDS = frozenset({'host.session_id', 'host.current_area_id'})

def observe_stub(field: str, *, campaign_id: str, branch_id: str,
                 host_epoch: int, build_fingerprint: str, adapter_version: str) -> Observation:
    """Synthetic-only: no connection to BG2:EE, and no mutation of host state."""
    status = Status.UNKNOWN if field in ALLOWED_FIELDS else Status.BLOCKED_CAPABILITY
    return Observation(campaign_id, branch_id, host_epoch, build_fingerprint,
                       adapter_version, field, status)
