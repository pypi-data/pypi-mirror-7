sostore is a straightforward storage engine for storing and retrieving 
dictionaries from an SQLite database.  Much of the terminology is taken
from MongoDB as this engine was originally designed to replace a PyMongo
implementation.

This library may seem trivial because it very much is.  However, some 
others may need a super-lightweight dictionary store.  Linking of 
objects within the database is not supported unless explicitly handled 
by the developer.

sostore is almost certainly not performant.  It can be thread-safe as 
long as Collection objects aren't passed around between threads as they
contain sqlite3.Connection objects.

More help is available at: http://sostore.readthedocs.org/en/latest/



