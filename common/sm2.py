from dataclasses import dataclass


@dataclass
class SM2Result:
    repetitions: int
    easiness_factor: float
    interval_days: int


def calculate_sm2(
    quality: int,
    repetitions: int,
    easiness_factor: float,
    interval_days: int,
) -> SM2Result:
    """
    Standard SM-2 (SuperMemo-2) scheduling update.

    quality: recall quality for this review, 0-5 (0 = complete blackout, 5 = perfect recall).
    """
    if quality < 3:
        # Failed recall: restart repetitions, review again tomorrow.
        repetitions = 0
        interval_days = 1
    else:
        if repetitions == 0:
            interval_days = 1
        elif repetitions == 1:
            interval_days = 6
        else:
            interval_days = round(interval_days * easiness_factor)
        repetitions += 1

    easiness_factor = easiness_factor + (
        0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )
    if easiness_factor < 1.3:
        easiness_factor = 1.3

    return SM2Result(
        repetitions=repetitions,
        easiness_factor=easiness_factor,
        interval_days=interval_days,
    )
