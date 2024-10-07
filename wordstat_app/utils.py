def letter_to_number(letter):
    """Преобразует букву в номер столбца (например, 'A' -> 1, 'B' -> 2)."""
    if not letter.isalpha() or len(letter) != 1:
        raise ValueError("Введена недопустимая буква")

    letter = letter.upper()
    return ord(letter) - ord('A') + 1
