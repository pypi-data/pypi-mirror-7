A find() method for SQLAlchemy

Usage::

    from sqlalchemy_find import SessionWithFind, QueryWithFind
    from sqlalchemy.orm import sessionmaker

    # Configure engine and sessionmaker
    engine = create_engine('postgresql://scott:tiger@localhost/')
    Session = sessionmaker(bind=engine,
                           class_=SessionWithFind,
                           query_cls=QueryWithFind)

    # Create a session
    session = Session()

    # Equivalent to:
    #   query = session.query(MyClass)
    #   query = query.filter(MyClass.name == 'foo')
    #   query = query.filter_by(is_active=True)
    query = session.find(MyClass, MyClass.name == 'foo', is_active=True)

    # Equivalent to:
    #   ob = session.query(MyClass).get(21)
    ob = session.get(MyClass, id=21)

