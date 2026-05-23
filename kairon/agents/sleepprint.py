"""動作確認用: print して 5 秒待ってまた print する。"""
import time
from datetime import datetime


def main() -> None:
    print(f"[sleepprint] start: {datetime.now():%Y-%m-%d %H:%M:%S}")
    time.sleep(5)
    print(f"[sleepprint] end:   {datetime.now():%Y-%m-%d %H:%M:%S}")


if __name__ == "__main__":
    main()
