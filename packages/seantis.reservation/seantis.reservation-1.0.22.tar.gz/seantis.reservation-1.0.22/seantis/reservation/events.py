from zope.interface import implements

from seantis.reservation.interfaces import (
    IResourceViewedEvent,
    IReservationBaseEvent,
    IReservationMadeEvent,
    IReservationApprovedEvent,
    IReservationDeniedEvent,
    IReservationRevokedEvent,
    IReservationsConfirmedEvent
)


class ResourceViewedEvent(object):
    implements(IResourceViewedEvent)

    def __init__(self, context):
        self.context = context


class ReservationBaseEvent(object):
    implements(IReservationBaseEvent)

    def __init__(self, reservation, language):
        self.reservation = reservation
        self.language = language


class ReservationMadeEvent(ReservationBaseEvent):
    implements(IReservationMadeEvent)


class ReservationApprovedEvent(ReservationBaseEvent):
    implements(IReservationApprovedEvent)


class ReservationDeniedEvent(ReservationBaseEvent):
    implements(IReservationDeniedEvent)


class ReservationRevokedEvent(ReservationBaseEvent):
    implements(IReservationRevokedEvent)

    def __init__(self, reservation, language, reason, send_email):
        super(ReservationRevokedEvent, self).__init__(reservation, language)
        self.reason = reason
        self.send_email = send_email


class ReservationsConfirmedEvent(object):
    implements(IReservationsConfirmedEvent)

    def __init__(self, reservations, language):
        self.reservations = reservations
        self.language = language
