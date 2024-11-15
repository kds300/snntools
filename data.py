import typing
from dataclasses import dataclass
from functools import partial


class Database:
    """Class for defining a basic dataclass-based database."""
    _entries: 'list[DatabaseEntry]'

    def __init__(self, entries:'list[DatabaseEntry]'=[]):
        """
        Parameters
        ----------
        entries: list[DatabaseEntry], Optional
            List containing the entries with which to initialize the database.
        """
        self._entries = []
        self._entries.extend(entries)

    def add_entries(self, entry: 'DatabaseEntry|list[DatabaseEntry]'):
        """Add the entry / entries to the database.

        Parameters
        ----------
        entry: DatabaseEntry | list[DatabaseEntry]
            The entry or list of entries to add to the database.
        """
        if isinstance(entry, DatabaseEntry):
            self._entries.append(entry)
        else:
            self._entries.extend(entry)

    def get_entries(self, **kwargs) -> 'Database':
        """Returns a Database containing all entries that satisfy the
        specified conditions.

        For each parameter, supply either a single value
        or a list of possible values to match the entries against.
        Unsupplied parameters will select all values for that parameter.

        Parameters
        ----------
        **kwargs
            Specify desired values for the attributes of the DatabaseEntry
            objects

        Returns
        -------
        database: Database
            Database object containing entries matching the conditions.
        """
        # convert inputs to list if required, ignoring 'None' values
        kw_filter = {}
        for key, val in kwargs.items():
            if not isinstance(val, list):
                val = [val,]
            kw_filter[key] = val

        _entries = filter(partial(self._filter_db, **kw_filter), self._entries)

        return Database(_entries)
    
    def get_attrs(self, attr:str) -> 'list':
        """Get the value of the specified attribute for each entry in the
        database.

        Parameters
        ----------
        attr: str
            Name of the data attribute for which to get the values

        Returns
        -------
            values: list
                List values corresponding to the specified attribute for each
                entry in the database
        """
        return [getattr(e, attr) for e in self._entries]

    @property
    def values(self) -> 'list[float]':
        """Return list of values for each entry in the database.

        Returns
        -------
        values: list[float]
            Returns list of the values for the `value` attribute of each entry
            in the database
        """
        return self.get_attrs(attr='value')

    def _filter_db(self, obj:'DatabaseEntry', **kwargs):
        """Helper function to filter iteratble of dataclass objects.
        **kwargs should contain keys corresponding to object attributes and
        values containing lists of attribute values to select for.
        Returns true if obj's attributes satisfy all requirements of kwargs.
        """
        return all(
            getattr(obj, key) in val for key, val in kwargs.items()
        )

    def __str__(self) -> str:
        return f"[{', '.join((str(e) for e in self._entries))}]"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"[{', '.join((str(e) for e in self._entries))}])"
        )

    def __getitem__(self, i:typing.SupportsIndex) -> 'DatabaseEntry':
        return self._entries[i]

    def __len__(self):
        return len(self._entries)


@dataclass(frozen=True)
class DatabaseEntry:
    """Basic entry for a database.

    Additional attributes can be added to further describe each entry.

    Attributes
    ----------
    label: str
        Identifier for the entry
    value: float
        Quantity for the entry
    """
    label: str
    value: float
