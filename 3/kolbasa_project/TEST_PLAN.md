# Test Plan: Каталог колбас – модуль представлений

## 1. Test Plan Identifier
TP-KOLBASA-VIEWS-2026

## 2. Introduction
Цель – проверка корректности отображения каталога колбас: маршруты, статус-коды, шаблоны, контекст, фильтрация и сортировка. 

## 3. Test Items
- product_list (список товаров)
- product_detail (детальная страница)
- about (страница «О сервисе»)

## 4. Features to be tested
- Доступность URL (GET 200)
- Корректность шаблонов
- Передача контекста (наличие ключей, данные)
- Фильтрация списка по типу колбасы
- Сортировка: по названию, весу, типу, количеству кусочков
- Пустой список
- 404 для несуществующего товара
- Статическая страница About содержит текст

## 5. Features NOT to be tested
- Авторизация и права доступа
- Формы создания/редактирования/удаления
- POST-запросы
- API

## 6. Approach
- Инструмент: `django.test.Client` (GET-запросы)
- Валидация: статус-коды, шаблоны, контекст (assertContains, assertTemplateUsed, проверка ключей)
- Тестовые данные создаются через `setUpTestData`

## 7. Item Pass/Fail Criteria
- Статус ответа 200 для существующих ресурсов, 404 для несуществующих
- Использован ожидаемый шаблон
- Контекст содержит требуемые ключи и корректные данные

## 8. Suspension Criteria
- Более 30% тестов завершились ошибкой
- Не удаётся подключиться к тестовой БД

## 9. Test Deliverables
- Код тестов: `catalog/tests/test_routes.py`, `catalog/tests/test_content.py`
- Отчёт о запуске: результат `python manage.py test catalog.tests --verbosity=2`
- Покрытие: `coverage report`

ID	    Сценарий	                            URL	                    Метод	Ожидаемый результат	                                    Приоритет
TC‑01	Главная страница каталога	            /	                    GET	    Status 200, шаблон product_list.html	                    High
TC‑02	Список содержит объекты	                /	                    GET	    Status 200, context['kolbasas'] не пуст	                    High
TC‑03	Фильтрация по типу колбасы	            /?kind=<id>	            GET	    Status 200, в списке только товары выбранного типа          High
TC‑04	Детальная страница товара	            /product/<pk>/	        GET	    Status 200, context['kolbasa'] существует                   High
TC‑05	Несуществующий товар	                /product/999/	        GET	    Status 404	                                                High
TC‑06	Страница «О сервисе»	                /about/	                GET	    Status 200, шаблон about.html	                            Medium
TC‑07	About содержит текст	                /about/	                GET	    assertContains находит фразу «О нашем сервисе»	            Medium
TC‑08	Пустой список товаров	                /	                    GET	    Status 200, context['kolbasas'] пуст	                    Medium
TC‑09	URL через reverse() (главная)	        reverse('product_list')	–	    Результат совпадает с '/'	                                Low
TC‑10	Контекст содержит обязательные ключи	/	                    GET	     context включает kolbasas, kinds, current_sort	            Medium
TC‑11	Страница групп по типу (kind_groups)	/kinds/	                GET	    Status 200, шаблон kind_groups.html, все типы в контексте	High
TC‑12	Корректное количество товаров в группах	/kinds/	                GET	     Для типа «варёная» 2 товара, «копчёная» — 1	            Medium