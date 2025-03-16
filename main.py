def main():
    print("Hello from anki-voice!")


if __name__ == "__main__":
    main()
    from aqt import gui_hooks

    def myfunc() -> None:
      print("myfunc")

    gui_hooks.reviewer_did_show_answer.append(myfunc)
