"""全機能をインポートしてレジストリに登録する。

新しい機能ファイルを足したら、ここに import を 1 行加えるだけでよい。
表示順はこの import 順になる。
"""

from features import (  # noqa: F401
    blog_writer,
    email_reply,
    summarizer,
    proofreader,
    tone_converter,
    sns_post,
    title_ideas,
)
