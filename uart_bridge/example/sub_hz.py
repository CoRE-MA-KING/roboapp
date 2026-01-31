import curses
import time
from collections import deque

import zenoh

# 監視対象のトピック
TOPICS = (
    "lidar/force_vector",
    "cam/switch",
    "damagepanel",
    "flap",
    "disks",
)


def main(stdscr: "curses.window") -> None:
    # 受信時刻を保持する辞書
    # key: topic_name, value: deque of timestamps
    topic_data: dict[str, deque[float]] = {topic: deque() for topic in TOPICS}

    def callback(sample: zenoh.Sample) -> None:
        key = str(sample.key_expr)
        if key in topic_data:
            topic_data[key].append(time.time())

    # Curses設定
    curses.curs_set(0)  # カーソル非表示
    stdscr.nodelay(True)  # 入力待ちしない
    stdscr.timeout(100)  # getchのタイムアウト(ms) -> 更新周期

    # Zenohセッション開始
    conf = zenoh.Config()
    with zenoh.open(conf) as session:
        # サブスクライバ登録
        _subs = []
        for topic in TOPICS:
            sub = session.declare_subscriber(topic, callback)
            _subs.append(sub)

        while True:
            # 終了判定 (qキー)
            c = stdscr.getch()
            if c == ord("q"):
                break

            # 画面描画
            stdscr.erase()
            stdscr.border()
            stdscr.addstr(0, 2, " Zenoh Topic Hz Monitor (Press 'q' to exit) ")

            current_time = time.time()
            row = 2

            # ヘッダー
            stdscr.addstr(row, 2, f"{'Topic':<25} | {'Hz':>6} | {'History (1s)':<20}")
            stdscr.addstr(row + 1, 2, "-" * 60)
            row += 2

            # 各トピックのHz計算と表示
            for topic in TOPICS:
                timestamps = topic_data[topic]

                # 直近1秒より古いデータを削除
                while timestamps and timestamps[0] < current_time - 1.0:
                    timestamps.popleft()

                hz = len(timestamps)

                # バーチャート表示 (最大30文字)
                bar_len = min(hz, 30)
                bar = "#" * bar_len

                # 表示
                # Topic名 | Hz | バー
                stdscr.addstr(row, 2, f"{topic:<25} | {hz:>6} | {bar}")

                row += 1

            stdscr.refresh()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
