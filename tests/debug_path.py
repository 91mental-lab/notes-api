import sys
import os

print("\n--- DEBUGGING SYS.PATH FOR PYTEST ---")
print(f"Current working directory: {os.getcwd()}")
print("sys.path during pytest run:")
for i, p in enumerate(sys.path):
    print(f"  {i}: {p}")

# Попробуем импортировать то, что вызывает ошибку, чтобы проверить
try:
    import src.auth
    print("Successfully imported src.auth")
except ModuleNotFoundError as e:
    print(f"FAILED to import src.auth: {e}")
except Exception as e:
    print(f"An unexpected error occurred during src.auth import: {type(e).__name__}: {e}")

print("--- END DEBUGGING ---")

# Это просто для того, чтобы pytest увидел какой-то тест
def test_debug_path_success():
    assert True