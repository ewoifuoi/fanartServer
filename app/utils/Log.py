
def Log(text):
    try:
        print("\033[35mSERVER\033[0m:\033[36m\t" + text + "\033[0m")
    except UnicodeEncodeError:
        # Replace unsupported characters with a safe placeholder
        print("\033[35mSERVER\033[0m:\033[36m\t" + text.encode('ascii', 'replace').decode() + "\033[0m")

def Error(text):
    try:
        print("\033[31mWARNING\033[0m:\033[33m " + text + "\033[0m")
    except UnicodeEncodeError:
        print("\033[31mWARNING\033[0m:\033[33m " + text.encode('ascii', 'replace').decode() + "\033[0m")