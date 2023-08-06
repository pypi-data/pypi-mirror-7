from datetime import timedelta

from sqlalchemy import types
from sqlalchemy.schema import Column
from sqlalchemy.schema import Index

from seantis.reservation import ORMBase
from seantis.reservation import Session
from seantis.reservation.models import customtypes
from seantis.reservation.models.other import OtherModels
from seantis.reservation.models.timestamp import TimestampMixin


class Reservation(TimestampMixin, ORMBase, OtherModels):
    """Describes a pending or approved reservation.

    """

    __tablename__ = 'reservations'

    id = Column(
        types.Integer(),
        primary_key=True,
        autoincrement=True
    )

    token = Column(
        customtypes.GUID(),
        nullable=False,
    )

    target = Column(
        customtypes.GUID(),
        nullable=False,
    )

    target_type = Column(
        types.Enum(u'group', u'allocation', name='reservation_target_type'),
        nullable=False
    )

    resource = Column(
        customtypes.GUID(),
        nullable=False
    )

    start = Column(
        types.DateTime(),
        nullable=True
    )

    end = Column(
        types.DateTime(),
        nullable=True
    )

    status = Column(
        types.Enum(u'pending', u'approved', name="reservation_status"),
        nullable=False
    )

    data = Column(
        customtypes.JSONEncodedDict(),
        nullable=True
    )

    email = Column(
        types.Unicode(254),
        nullable=False
    )

    session_id = Column(
        customtypes.GUID()
    )

    quota = Column(
        types.Integer(),
        nullable=False
    )

    __table_args__ = (
        Index('target_status_ix', 'status', 'target', 'id'),
    )

    def _target_allocations(self):
        """ Returns the allocations this reservation is targeting. This should
        NOT be confused with db.allocations_by_reservation. The method in
        the db module returns the actual allocations belonging to an approved
        reservation.

        This method only returns the master allocations to get information
        about timespans and other properties. If you don't know exactly
        what you're doing you do not want to use this method as misuse might
        be dangerous.

        """
        Allocation = self.models.Allocation
        query = Session.query(Allocation)
        query = query.filter(Allocation.group == self.target)

        # master allocations only
        query = query.filter(Allocation.resource == Allocation.mirror_of)

        return query

    def timespans(self, start=None, end=None):

        if self.target_type == u'allocation':
            return [(self.start, self.end + timedelta(microseconds=1))]
        elif self.target_type == u'group':
            return [
                (
                    a.display_start, a.display_end
                )
                for a in self._target_allocations()
            ]
        else:
            raise NotImplementedError

    @property
    def title(self):
        return self.email

    @property
    def autoapprovable(self):
        query = self._target_allocations()
        query = query.filter(self.models.Allocation.approve_manually == True)

        # A reservation is deemed autoapprovable if no allocation
        # requires explicit approval

        return query.first() is None
