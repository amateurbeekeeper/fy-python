import unittest
import re
import sys


class StockError(Exception):
    pass


class StockManager:
    def __init__(self):
        self.stock = {}

    def validate_sku(self, sku):
        # Check if SKU format is valid (Example: AB-6).
        if not re.match(r"^[A-Z]{1,3}-[0-9]{1,3}$", sku):
            raise StockError(f"👎 Invalid SKU format: {sku}")

    def validate_amount(self, amount):
        # Check if amount is a positive integer and doesn't exceed 3 digits.
        if not amount.isdigit() or not (0 <= int(amount) <= 999):
            raise StockError(f"👎 Invalid amount format: {amount}")

    def process_command(self, instruction):
        parts = instruction.split()
        operation = parts[0]
        sku_and_amount_pairs = parts[1:]

        if operation == 'set-stock':
            self.process_set_stock(sku_and_amount_pairs)
        elif operation == 'add-stock':
            self.process_add_stock(sku_and_amount_pairs)
        elif operation == 'order':
            self.process_order(sku_and_amount_pairs)
        else:
            raise StockError(f"👎 Unknown command: {operation}")

    def process_set_stock(self, parts):
        skus = parts[::2]
        amounts = parts[1::2]
        for sku, amount in zip(skus, amounts):
            try:
                self.validate_sku(sku)
                self.validate_amount(amount)
            except StockError:
                continue
            else:
                self.stock[sku] = int(amount)

    def process_add_stock(self, parts):
        skus = parts[::2]
        amounts = parts[1::2]
        for sku, amount in zip(skus, amounts):
            try:
                self.validate_sku(sku)
                self.validate_amount(amount)
            except StockError:
                continue
            else:
                if sku not in self.stock:
                    raise StockError(
                        f"👎 SKU {sku} not found, cannot add stock")
                else:
                    self.stock[sku] += int(amount)

    def process_order(self, parts):
        order_ref = parts[0]
        skus = parts[1::2]
        amounts = parts[2::2]
        for sku, amount in zip(skus, amounts):
            try:
                self.validate_sku(sku)
                self.validate_amount(amount)
            except StockError:
                continue
            else:
                if sku not in self.stock:
                    raise StockError(
                        f"👎 SKU {sku} not found, cannot place order")
                elif self.stock[sku] < int(amount):
                    raise StockError(
                        f"👎 Insufficient stock for order {order_ref}, SKU: {sku}")
                else:
                    self.stock[sku] -= int(amount)

    def print_stock(self):
        sorted_stock = sorted(self.stock.items())
        for sku, level in sorted_stock:
            print(f"{sku} {level}")


def process_stock_file(filename):
    stock_manager = StockManager()
    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            print(f"🔍 Processing instruction {line_number}: {line}")
            try:
                stock_manager.process_command(line)
            except StockError as e:
                print(
                    f"❌❌❌ Error processing instruction {line_number}: {line}")
                print(f"   {e}")

    # Print final stock levels after processing all commands.
    print("\n📊 Final Stock Levels:")
    stock_manager.print_stock()


class TestStockManager(unittest.TestCase):
    def setUp(self):
        self.stock_manager = StockManager()

    def test_set_stock(self):
        self.stock_manager.process_command("set-stock AB-6 100 CD-3 200")
        self.assertEqual(self.stock_manager.stock["AB-6"], 100)
        self.assertEqual(self.stock_manager.stock["CD-3"], 200)

    def test_add_stock(self):
        self.stock_manager.process_command("set-stock AB-6 100")
        self.stock_manager.process_command("add-stock AB-6 20")
        self.assertEqual(self.stock_manager.stock["AB-6"], 120)

    def test_process_order(self):
        self.stock_manager.process_command("set-stock AB-6 100")
        self.stock_manager.process_command("order ON-123 AB-6 50")
        self.assertEqual(self.stock_manager.stock["AB-6"], 50)

    def test_insufficient_stock_order(self):
        with self.assertRaises(StockError):
            self.stock_manager.process_command("set-stock AB-6 100")
            self.stock_manager.process_command("order ON-123 AB-6 150")

    def test_multiple_order_skus(self):
        self.stock_manager.process_command("set-stock AB-6 100 CD-3 50")
        self.stock_manager.process_command("order ON-123 AB-6 20 CD-3 30")
        self.assertEqual(self.stock_manager.stock["AB-6"], 80)
        self.assertEqual(self.stock_manager.stock["CD-3"], 20)

    def test_add_stock_new_sku(self):
        with self.assertRaises(StockError):
            self.stock_manager.process_command("add-stock AB-6 20")

    def test_add_stock_existing_sku(self):
        self.stock_manager.process_command("set-stock AB-6 100")
        self.stock_manager.process_command("add-stock AB-6 20")
        self.assertEqual(self.stock_manager.stock["AB-6"], 120)

    def test_invalid_sku_format(self):
        with self.assertRaises(StockError):
            self.stock_manager.validate_sku("AB_6")

    def test_invalid_amount_format_float(self):
        with self.assertRaises(StockError):
            self.stock_manager.validate_amount("10.5")

    def test_invalid_amount_format_negative(self):
        with self.assertRaises(StockError):
            self.stock_manager.validate_amount("-10")

    def test_unknown_command(self):
        with self.assertRaises(StockError) as context:
            self.stock_manager.process_command("unknown-command AB-6 100")
        self.assertTrue("Unknown command" in str(context.exception))

    def test_invalid_sku_format_with_numbers(self):
        with self.assertRaises(StockError) as context:
            self.stock_manager.validate_sku("A1-6")
        self.assertTrue("Invalid SKU format" in str(context.exception))

    def test_invalid_sku_format_with_extra_hyphen(self):
        with self.assertRaises(StockError) as context:
            self.stock_manager.validate_sku("AB--6")
        self.assertTrue("Invalid SKU format" in str(context.exception))

    def test_order_with_unknown_sku(self):
        # Test for ordering with an SKU that was never set.
        with self.assertRaises(StockError) as context:
            self.stock_manager.process_command("order ON-124 ZF-9 10")
        self.assertTrue("SKU ZF-9 not found" in str(context.exception))

    def test_multiple_invalid_commands(self):
        with self.assertRaises(StockError):
            self.stock_manager.process_command("set-stock AB-6 1000")
        with self.assertRaises(StockError):
            self.stock_manager.process_command("add-stock ZF-9 20")
        with self.assertRaises(StockError):
            self.stock_manager.process_command("order ON-123 ZF-9 150")

    def test_stock_after_invalid_operation(self):
        # Test to ensure stock levels aren't altered after invalid operations.
        with self.assertRaises(StockError):
            self.stock_manager.process_command("set-stock AB-6 1000")
        self.assertNotIn("AB-6", self.stock_manager.stock)

    def test_order_then_add_stock(self):
        # Test to check stock levels after an invalid order and then a stock addition.
        self.stock_manager.process_command("set-stock AB-6 100")
        with self.assertRaises(StockError):
            self.stock_manager.process_command("order ON-123 AB-6 150")
        self.stock_manager.process_command("add-stock AB-6 50")
        self.assertEqual(self.stock_manager.stock["AB-6"], 150)


# Main method to determine if the script is run as a standalone script or imported as a module.
if __name__ == "__main__":
    # If a file is provided as an argument, process that file.
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        process_stock_file(input_file)
    else:
        # If no file is provided, run the unit tests.
        unittest.main()
