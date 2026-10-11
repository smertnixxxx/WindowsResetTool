"""
Windows Reset & Reinstall Automation Tool
Скрипт для безопасного сброса или переустановки Windows 10/11 без внешнего USB-накопителя.
Использует встроенную утилиту Windows Recovery Environment (WinRE): systemreset.exe.
"""

import ctypes
import os
import subprocess
import sys


def is_admin() -> bool:
    """Проверяет, запущен ли скрипт с правами администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        return False


def elevate_privileges():
    """Запрашивает повышение прав через диалог UAC, если скрипт запущен без прав администратора."""
    if is_admin():
        return

    print("[*] Требуются права администратора. Запрос повышения привилегий UAC...")
    
    if getattr(sys, "frozen", False):
        executable = sys.executable
        params = " ".join(f'"{arg}"' for arg in sys.argv[1:])
    else:
        executable = sys.executable
        params = f'"{sys.argv[0]}" ' + " ".join(f'"{arg}"' for arg in sys.argv[1:])

    # Запуск с глаголом runas вызывает диалог UAC
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    
    # При коде > 32 процесс успешно запущен с правами администратора
    if ret > 32:
        sys.exit(0)
    else:
        print("[-] Запрос прав отклонён пользователем.")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)


def get_systemreset_path() -> str:
    """
    Возвращает корректный путь к systemreset.exe.
    Учитывает перенаправление SysWOW64 при запуске 32-битного процесса в 64-битной Windows.
    """
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    
    # Проверка виртуальной папки Sysnative (для 32-битных процессов на x64)
    sysnative_path = os.path.join(system_root, "Sysnative", "systemreset.exe")
    if os.path.exists(sysnative_path):
        return sysnative_path
        
    system32_path = os.path.join(system_root, "System32", "systemreset.exe")
    if os.path.exists(system32_path):
        return system32_path
        
    raise FileNotFoundError("Системная утилита systemreset.exe не найдена на этом компьютере.")


def main():
    elevate_privileges()

    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 65)
    print("      МАСТЕР ПЕРЕУСТАНОВКИ / СБРОСА WINDOWS 10 / 11")
    print("=" * 65)
    print("\nВНИМАНИЕ!")
    print("Данная утилита запускает официальный системный мастер восстановления Windows.")
    print("Процедура выполняется без флешки (через раздел WinRE или облако Microsoft).")
    print("\nВ процессе вам будет предложено:")
    print("  1. Сохранить личные файлы или очистить диск полностью.")
    print("  2. Выбрать локальную переустановку или загрузку свежей версии из облака.")
    print("=" * 65)

    print("\nДоступные режимы:")
    print(" [1] Полный сброс / переустановка (systemreset -factoryreset) [Рекомендуется]")
    print(" [2] Новый запуск / Fresh Start (systemreset -cleanpc)")
    print(" [0] Отмена и выход")

    choice = input("\nВыберите действие (0, 1 или 2): ").strip()

    if choice == "1":
        mode_flag = "-factoryreset"
    elif choice == "2":
        mode_flag = "-cleanpc"
    else:
        print("[*] Операция отменена пользователем.")
        return

    print("\n" + "!" * 65)
    print("ПОДТВЕРЖДЕНИЕ БЕЗОПАСНОСТИ:")
    print("Убедитесь, что важные данные сохранены или выбрана опция сохранения файлов.")
    confirm = input('Для продолжения введите слово "СБРОС" (заглавными буквами): ').strip()
    print("!" * 65)

    if confirm != "СБРОС":
        print("\n[*] Подтверждение не совпало. Отмена операции.")
        return

    try:
        exe_path = get_systemreset_path()
        print(f"\n[+] Запуск системного мастера: {exe_path} {mode_flag}...")
        
        # Запускаем системный процесс
        subprocess.Popen([exe_path, mode_flag], close_fds=True)
        print("[+] Мастер восстановления Windows успешно запущен.")
        print("[*] Следуйте шагам официального интерфейса Windows.")

    except Exception as e:
        print(f"\n[-] Ошибка при запуске: {e}")
        input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
