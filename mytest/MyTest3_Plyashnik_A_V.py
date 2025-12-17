""" 
    Задание на зачёт, вы сказали сделать тест 3 без пунктов 4,5,8 и тест 4 (след файл)
    Надеюсь я правильно понял задание, если что-то ещё нужно, пишите
"""

import pytest
from datetime import datetime, timedelta
from library_system import (
    Book, Reader, Library,
    BookNotAvailableError, ReaderNotFoundError,
    create_sample_library
)

# ============= ТЕСТЫ КЛАССА BOOK =============

class TestBook:
    """Тесты для класса Book"""
   
    def test_should_create_book_with_valid_data(self):
        """Тест: создание книги с корректными данными"""
        book = Book("978-0-123456-78-9", "Название", "Автор", 2020, 5)
       
        assert book.isbn == "978-0-123456-78-9"
        assert book.title == "Название"
        assert book.author == "Автор"
        assert book.year == 2020
        assert book.total_copies == 5
        assert book.available_copies == 5
   
    def test_should_raise_error_for_empty_isbn(self):
        """Тест: пустой ISBN вызывает ValueError"""
        with pytest.raises(ValueError, match="ISBN, название и автор обязательны"):
            Book("", "Название", "Автор", 2020)
   
    def test_should_raise_error_for_empty_title(self):
        """Тест: пустое название вызывает ValueError"""
        with pytest.raises(ValueError, match="ISBN, название и автор обязательны"):
            Book("978-0-123456-78-9", "", "Автор", 2020)
   
    def test_should_raise_error_for_empty_author(self):
        """Тест: пустой автор вызывает ValueError"""
        with pytest.raises(ValueError, match="ISBN, название и автор обязательны"):
            Book("978-0-123456-78-9", "Название", "", 2020)
   
    def test_should_raise_error_for_negative_copies(self):
        """Тест: отрицательное количество копий вызывает ValueError"""
        with pytest.raises(ValueError, match="Количество копий не может быть отрицательным"):
            Book("978-0-123456-78-9", "Название", "Автор", 2020, -1)


# ============= ТЕСТЫ КЛАССА READER =============

class TestReader:
    """Тесты для класса Reader"""
   
    def test_should_create_reader_with_valid_data(self):
        """Тест: создание читателя с корректными данными"""
        reader = Reader("R001", "Иван Иванов", "ivan@example.com")
       
        assert reader.reader_id == "R001"
        assert reader.name == "Иван Иванов"
        assert reader.email == "ivan@example.com"
        assert reader.borrowed_books == []
        assert reader.history == []
   
    def test_should_raise_error_for_empty_reader_id(self):
        """Тест: пустой reader_id вызывает ValueError"""
        with pytest.raises(ValueError, match="ID, имя и email обязательны"):
            Reader("", "Имя", "email@example.com")
   
    def test_should_raise_error_for_empty_name(self):
        """Тест: пустое имя вызывает ValueError"""
        with pytest.raises(ValueError, match="ID, имя и email обязательны"):
            Reader("R001", "", "email@example.com")
   
    def test_should_raise_error_for_empty_email(self):
        """Тест: пустой email вызывает ValueError"""
        with pytest.raises(ValueError, match="ID, имя и email обязательны"):
            Reader("R001", "Имя", "")


# ============= ТЕСТЫ КЛАССА LIBRARY =============

class TestLibrary:
    """Тесты для класса Library"""
   
    def test_should_create_library_with_valid_name(self):
        """Тест: создание библиотеки с корректным названием"""
        library = Library("Городская библиотека")
       
        assert library.name == "Городская библиотека"
        assert library.books == {}
        assert library.readers == {}
        assert library.active_loans == {}
   
    def test_should_raise_error_for_empty_name(self):
        """Тест: пустое название вызывает ValueError"""
        with pytest.raises(ValueError, match="Название библиотеки обязательно"):
            Library("")
       

# ============= ДОПОЛНИТЕЛЬНЫЕ EDGE CASE ТЕСТЫ =============

class TestEdgeCases:
    """Тесты граничных случаев"""
   
    def test_book_with_zero_copies(self):
        """Тест: книга с 0 копий при создании"""
        book = Book("978-0-123456-78-9", "Книга", "Автор", 2020, 0)
       
        assert book.total_copies == 0
        assert book.available_copies == 0
        assert book.is_available() is False
   
    def test_library_with_special_characters_in_name(self):
        """Тест: библиотека с спецсимволами в названии"""
        library = Library("Библиотека №1 «Центральная» (г. Москва)")
       
        assert library.name == "Библиотека №1 «Центральная» (г. Москва)"
   
    def test_reader_with_multiple_at_signs_in_email(self):
        """Тест: email с несколькими @ должен быть валиден"""
        # В реальности email может иметь @ только один раз, но наша простая
        # валидация просто проверяет наличие @
        reader = Reader("R001", "Имя", "test@@example.com")
        assert reader.email == "test@@example.com"
   
    def test_book_title_with_numbers_and_symbols(self):
        """Тест: название книги с цифрами и символами"""
        book = Book("978-0-123456-78-9", "2001: Космическая одиссея", "А. Кларк", 2000, 1)
       
        assert book.title == "2001: Космическая одиссея"
   
    def test_return_same_book_twice(self):
        """Тест: попытка вернуть одну и ту же книгу дважды"""
        library = Library("Библиотека")
        book = Book("978-0-123456-78-9", "Книга", "Автор", 2020, 1)
        reader = Reader("R001", "Читатель", "reader@example.com")
       
        library.add_book(book)
        library.register_reader(reader)
       
        # Берем и возвращаем
        library.borrow_book("R001", "978-0-123456-78-9")
        success1, _ = library.return_book("R001", "978-0-123456-78-9")
       
        # Попытка вернуть снова
        success2, fine2 = library.return_book("R001", "978-0-123456-78-9")
       
        assert success1 is True
        assert success2 is False
        assert fine2 == 0.0
   
    def test_get_popular_books_with_tied_counts(self):
        """Тест: популярные книги с одинаковым количеством займов"""
        library = Library("Библиотека")
       
        # Добавляем 3 книги
        for i in range(1, 4):
            book = Book(f"978-{i}", f"Книга {i}", "Автор", 2020, 2)
            library.add_book(book)
       
        # Добавляем 3 читателей
        for i in range(1, 4):
            reader = Reader(f"R00{i}", f"Читатель {i}", f"reader{i}@example.com")
            library.register_reader(reader)
       
        # Каждый читатель берет свою книгу (по 1 разу каждая)
        library.borrow_book("R001", "978-1")
        library.borrow_book("R002", "978-2")
        library.borrow_book("R003", "978-3")
       
        popular = library.get_popular_books(top_n=3)
       
        # Все три книги должны иметь счетчик 1
        assert len(popular) == 3
        assert all(count == 1 for _, count in popular)
   
    def test_statistics_for_reader_with_no_activity(self):
        """Тест: статистика для читателя без активности"""
        library = Library("Библиотека")
        reader = Reader("R001", "Читатель", "reader@example.com")
        library.register_reader(reader)
       
        stats = library.get_reader_stats("R001")
       
        assert stats['currently_borrowed'] == 0
        assert stats['total_borrowed'] == 0
        assert stats['total_returned'] == 0
        assert stats['current_fines'] == 0.0
   
    def test_very_long_overdue_period(self, monkeypatch):
        """Тест: очень долгая просрочка"""
        library = Library("Библиотека")
        book = Book("978-0-123456-78-9", "Книга", "Автор", 2020, 1)
        reader = Reader("R001", "Читатель", "reader@example.com")
       
        library.add_book(book)
        library.register_reader(reader)
       
        # Дата выдачи
        class MockDatetimeBorrow:
            @staticmethod
            def now():
                return datetime(2024, 1, 1, 12, 0, 0)
       
        monkeypatch.setattr('library_system.datetime', MockDatetimeBorrow)
        library.borrow_book("R001", "978-0-123456-78-9")
       
        # Возврат через год
        class MockDatetimeReturn:
            @staticmethod
            def now():
                return datetime(2025, 1, 1, 12, 0, 0)
       
        monkeypatch.setattr('library_system.datetime', MockDatetimeReturn)
       
        success, fine = library.return_book("R001", "978-0-123456-78-9")
       
        # Вычисляем точную разницу дней между датами
        due_date = datetime(2024, 1, 1, 12, 0, 0) + timedelta(days=14)
        return_date = datetime(2025, 1, 1, 12, 0, 0)
        overdue_days = (return_date - due_date).days
        expected_fine = overdue_days * 10.0
       
        assert success is True
        assert fine == pytest.approx(expected_fine)

# ============= ТЕСТЫ ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ =============

class TestHelperFunctions:
    """Тесты вспомогательных функций"""
   
    def test_create_sample_library(self):
        """Тест: функция create_sample_library создает корректную библиотеку"""
        library = create_sample_library()
       
        assert library.name == "Городская библиотека"
        assert len(library.books) == 3
        assert len(library.readers) == 2
       
        # Проверяем наличие конкретных книг
        assert "978-0-545-01022-1" in library.books
        assert "978-5-17-084716-3" in library.books
       
        # Проверяем читателей
        assert "R001" in library.readers
        assert "R002" in library.readers


if __name__ == "__main__":
    # Запуск тестов с подробным выводом
    pytest.main([__file__, "-v", "--tb=short"])
