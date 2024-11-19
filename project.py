import os
import csv


class PriceMachine:
    def __init__(self):
        self.data = []  # Список для хранения данных из всех прайс-листов
        self.result = ''
        self.name_length = 0

    def load_prices(self, file_path=''):
        """
        Сканирует указанный каталог. Ищет файлы со словом 'price' в названии.
        В файлах ищет столбцы с названием товара, ценой и весом.
        """
        if not os.path.isdir(file_path):
            return "Указанный путь не является каталогом."

        files = [f for f in os.listdir(file_path) if "price" in f.lower() and f.endswith(".csv")]

        if not files:
            return "Файлы прайс-листов не найдены."

        combined_data = []
        for file in files:
            file_path_full = os.path.join(file_path, file)
            #print(file_path_full)
            try:
                with open(file_path_full, encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    headers = next(reader)
                    product_col, price_col, weight_col = self._search_product_price_weight(headers)

                    if product_col is not None and price_col is not None and weight_col is not None:
                        for row in reader:
                            try:
                                product = row[product_col]
                                price = float(row[price_col])
                                weight = float(row[weight_col])
                                price_per_kg = price / weight
                                combined_data.append(
                                    {"name": product, "price": price, "weight": weight, "file": file,
                                     "price_per_kg": price_per_kg})
                            except (ValueError, IndexError):
                                continue
            except Exception as e:
                print(f"Ошибка обработки файла {file}: {e}")

        self.data = sorted(combined_data, key=lambda x: x["price_per_kg"])
        return f"Загружено {len(self.data)} позиций из {len(files)} файлов."

    def _search_product_price_weight(self, headers):
        """
        Определяет индексы столбцов с названием, ценой и весом.
        """
        headers_lower = [h.lower() for h in headers]
        product_col = next((i for i, h in enumerate(headers_lower) if h in ["товар", "название", "наименование", "продукт"]), None)
        price_col = next((i for i, h in enumerate(headers_lower) if h in ["цена", "розница"]), None)
        weight_col = next((i for i, h in enumerate(headers_lower) if h in ["вес", "масса", "фасовка"]), None)
        return product_col, price_col, weight_col

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует данные в HTML файл.
        """
        if not self.data:
            return "Нет данных для экспорта."

        rows = ""
        for i, item in enumerate(self.data, start=1):
            rows += f"""
                <tr>
                    <td>{i}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            """

        result = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
                {rows}
            </table>
        </body>
        </html>
        """

        with open(fname, "w", encoding="utf-8") as f:
            f.write(result)
        return f"Данные успешно экспортированы в файл {fname}."

    def find_text(self, text):
        """
        Ищет записи, содержащие текст, в названиях продуктов.
        """

        if not self.data:
            return "Нет данных для поиска."

        filtered_data = [item for item in self.data if text.lower() in item["name"].lower()]
        if not filtered_data:
            return "Ничего не найдено."

        filtered_data.sort(key=lambda x: x["price_per_kg"])
        result_table = "№\tНаименование\t\tЦена\tВес\tФайл\tЦена за кг.\n"
        for i, item in enumerate(filtered_data, start=1):
            result_table += f"{i}\t{item['name'][:30]}\t{item['price']}\t{item['weight']}\t{item['file']}\t{item['price_per_kg']:.2f}\n"
        return result_table


# Использование
if __name__ == "__main__":
    pm = PriceMachine()
    folder_path = "price/"  # Укажите путь к папке с файлами

    print(pm.load_prices(folder_path))  # Загружаем прайс-листы

    while True:
        search_text = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        if search_text.lower() == "exit":
            print("Работа завершена.")
            break
        print(pm.find_text(search_text))  # Выполняем поиск

    print(pm.export_to_html())  # Экспортируем данные в HTML
