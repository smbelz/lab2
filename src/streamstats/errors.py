class StreamStatsError(Exception):
    """Базовое исключение."""

class StreamStatsParseError(StreamStatsError):
    """Ошибка парсинга строки."""

class StreamStatsTimestampError(StreamStatsError):
    """Неверная временная метка."""

class UnsupportedFileTypeError(StreamStatsError):
    """Неподдерживаемый формат."""