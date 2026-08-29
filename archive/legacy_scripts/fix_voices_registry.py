"""
fix_voices_registry.py
Run as ADMINISTRATOR.
Copies Windows OneCore voices (Kalpana, etc.) into the legacy SAPI5 registry
so pyttsx3 can see and use them.
Must be run with: Right-click > Run as Administrator
"""
import winreg
import sys

def clean_old_sapi():

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            SAPI5_PATH,
            0,
            winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY
        )

        remove=[]

        i=0

        while True:
            try:
                name=winreg.EnumKey(key,i)

                if "david" in name.lower():
                    remove.append(name)

                i+=1

            except OSError:
                break


        for r in remove:
            winreg.DeleteKey(
                key,
                r
            )
            print("Removed:",r)

        winreg.CloseKey(key)


    except Exception as e:
        print("Cleanup error:",e)

ONECORE_PATH = r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"
SAPI5_PATH   = r"SOFTWARE\Microsoft\Speech\Voices\Tokens"

def copy_voice_key(src_key, dest_key_path, voice_name):
    try:
        dest_full = dest_key_path + "\\" + voice_name
        # Create destination key
        dest = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, dest_full,
                                  0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
        # Copy all values
        i = 0
        while True:
            try:
                name, data, dtype = winreg.EnumValue(src_key, i)
                winreg.SetValueEx(dest, name, 0, dtype, data)
                i += 1
            except OSError:
                break
        # Copy Attributes subkey if exists
        try:
            src_attr = winreg.OpenKey(src_key, "Attributes",
                                      0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            dest_attr = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE,
                                           dest_full + "\\Attributes",
                                           0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            j = 0
            while True:
                try:
                    n, d, t = winreg.EnumValue(src_attr, j)
                    winreg.SetValueEx(dest_attr, n, 0, t, d)
                    j += 1
                except OSError:
                    break
            winreg.CloseKey(src_attr)
            winreg.CloseKey(dest_attr)
        except OSError:
            pass
        winreg.CloseKey(dest)
        return True
    except PermissionError:
        return "permission"
    except Exception as e:
        return str(e)

def main():
    print("=" * 60)
    print("Cleaning old broken voices...")
    clean_old_sapi()
    print("  JARVIS Voice Registry Fix")
    print("  Copying OneCore voices -> SAPI5 registry")
    print("=" * 60)

    try:
        onecore = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, ONECORE_PATH,
            0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
    except FileNotFoundError:
        print("\nOneCore voices path not found.")
        print("No additional voices installed yet.")
        input("Press Enter to exit...")
        return
    except PermissionError:
        print("\nERROR: Permission denied.")
        print("Please run this script as ADMINISTRATOR:")
        print("  Right-click check_voices.py > Run as administrator")
        input("Press Enter to exit...")
        return

    # List all voices in OneCore
    voices_found = []
    i = 0
    while True:
        try:
            name = winreg.EnumKey(onecore, i)
            voices_found.append(name)
            i += 1
        except OSError:
            break

    if not voices_found:
        print("\nNo OneCore voices found to copy.")
        winreg.CloseKey(onecore)
        input("Press Enter to exit...")
        return

    print(f"\nFound {len(voices_found)} OneCore voice(s):")
    for v in voices_found:
        print(f"  - {v}")

    print("\nCopying to SAPI5 registry...")
    for voice_name in voices_found:
        try:
            src = winreg.OpenKey(onecore, voice_name,
                                 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            result = copy_voice_key(src, SAPI5_PATH, voice_name)
            winreg.CloseKey(src)
            if result is True:
                print(f"  OK   {voice_name}")
            elif result == "permission":
                print(f"  ERR  {voice_name} - Run as Administrator!")
            else:
                print(f"  ERR  {voice_name} - {result}")
        except Exception as e:
            print(f"  ERR  {voice_name} - {e}")

    winreg.CloseKey(onecore)

    print("\n" + "=" * 60)
    print("  DONE! Ab python check_voices.py run karo")
    print("  Naye voices list mein dikhenge.")
    print("  (Restart ki zaroorat NAHI hai)")
    print("=" * 55)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("Ye script sirf Windows pe chalegi.")
    else:
        main()
