from tools.windows_app_scanner import WindowsAppScanner

scanner = WindowsAppScanner()

apps = scanner.all()

print()

print("Installed Apps:", len(apps))

print()

for name in list(apps.keys())[:50]:

    print(name)