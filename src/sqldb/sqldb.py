def get_sql_engine():
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL
    from general.general import get_env_vars
    from urllib.parse import quote_plus as urlquote
    
    DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME = get_env_vars(
        ['DB_DRIVER',
        'DB_USER',
        'DB_PASS',
        'DB_HOST',
        'DB_PORT',
        'DB_NAME'],
        return_type='tuple')

    DB_STRING = URL.create(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        database=DB_NAME,
        port=DB_PORT
    )

    engine = create_engine(DB_STRING)
    return engine
