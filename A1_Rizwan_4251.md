# Name: Maaz Rizwan
# ID: 20424251

| Function Name                   | Implementation Status | What is Missing (if any)                   |
|---------------------------------|---------------------|--------------------------------------------|
| create_app                       | Complete            | Complete                                   |
| init_database                     | Complete            | Complete                                   |
| add_sample_data                   | Complete            | Complete                                   |
| get_db_connection                 | Complete            | Complete                                   |
| get_all_books                     | Complete            | Complete                                   |
| get_book_by_id                    | Complete            | Complete                                   |
| get_book_by_isbn                  | Complete            | Complete                                   |
| get_patron_borrowed_books         | Complete            | Complete                                   |
| get_patron_borrow_count           | Complete            | Complete                                   |
| insert_book                       | Complete            | Complete                                   |
| insert_borrow_record              | Complete            | Complete                                   |
| update_book_availability          | Complete            | Complete                                   |
| update_borrow_record_return_date  | Complete            | Complete                                   |
| add_book_to_catalog               | Complete            | Complete                                   |
| borrow_book_by_patron             | Complete            | Complete                                   |
| return_book_by_patron             | Partial             | Logic for returning book not implemented   |
| calculate_late_fee_for_book       | Partial             | Late fee calculator not implemented        |
| search_books_in_catalog           | Partial             | Catalog search not implemented             |
| get_patron_status_report          | Partial             | patron status report logic not implemented |


## Tests Summaries
- **get_patron_status_report.py** – Tests the patron status report function including borrowed books and total borrow count 
- **test_add_book_to_catalog.py** –Tests function to add book to catalog, validating title, author, ISBN and total # of copies 
- **test_borrow_books_by_patron.py** – Test book borrowing feature by testing Valid patron ID, book availability and if patron has exceeded borrowing limit 
- **test_calculate_late_fee_for_book.py** – Tests late fee calculations for borrowed books by factoring length of book being overdue and other valid inputs
- **test_return_book_by_patron.py** –Tests returning books. Checks if reutrns are valid and if information like patron ID is valid too. 
- **test_search_books_in_catalog.py** – Tests all ways to search books in catalog; title, author, ISBN and other valid search types
