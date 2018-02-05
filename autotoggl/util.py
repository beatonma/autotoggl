def midnight(datetime):
    try:
        return datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    except:
        return datetime
