from brain.response_handler import ResponseHandler


def run_test(command, result):

    reply = ResponseHandler.handle(command, result)

    print()
    print("COMMAND :", command)
    print("RESULT  :", result)
    print("REPLY   :", reply)


if __name__ == "__main__":

    run_test(
        "open chrome",
        {
            "status": "success",
            "type": "installed_app",
            "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        }
    )

    run_test(
        "search youtube lofi music",
        {
            "status": "success",
            "type": "website",
            "name": "youtube",
            "query": "lofi music"
        }
    )

    run_test(
        "close chrome",
        {
            "status": "success",
            "type": "close",
            "name": "chrome"
        }
    )

    run_test(
        "open my pictures",
        {
            "status": "success",
            "type": "file_launcher",
            "target": "pictures",
            "path": r"C:\Users\hp\Pictures",
            "kind": "folder"
        }
    )

    run_test(
        "minimize chrome",
        {
            "status": "success",
            "type": "minimize",
            "name": "chrome"
        }
    )

    run_test(
        "test failure",
        {
            "status": "error",
            "message": "Application not found"
        }
    )