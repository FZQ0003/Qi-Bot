from typing import Callable

from creart import create
from launart import Service, Launart


def __new_scheduler_service():
    from graia.scheduler import GraiaScheduler
    from graia.scheduler.service import SchedulerService
    return SchedulerService(create(GraiaScheduler))


MAPPING_NEW_SERVICE: dict[str, Callable[[], Service]] = {
    'scheduler.service': __new_scheduler_service
}


def add_service(manager: Launart, service: str | type[Service] | Service) -> None:
    if isinstance(service, Service):
        s_id = service.id

        def s_new() -> Service:
            return service
    elif isinstance(service, str):
        s_id = service
        s_new = MAPPING_NEW_SERVICE.get(s_id)
    else:
        s_id = service.id
        s_new = MAPPING_NEW_SERVICE.get(s_id, lambda: service())
    if s_new:
        manager.add_component(s_new())
    else:
        raise ImportError(f'Service not found in mapping: {s_id}')


def add_available_services(manager: Launart) -> None:
    for service in MAPPING_NEW_SERVICE:
        try:
            add_service(manager, service)
        except ImportError or ValueError:
            ...
