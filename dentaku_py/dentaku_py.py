class Token:
    #このクラスを利用して、数式から検出された、意味を持つ単語の最小単位である数値や加算減算などの記号、括弧などを使いやすい形で管理する。
    def __init__(self,data):#コンストラクタ
        self.isNumber=0#数値であるかどうかの情報、1or0
        self.isCommand=0#加減算、乗算除算などの記号であるかの情報、1or0
        self.text=""#データを文字で置いておく
        self.number=0.0#数値データの場合は数値に変わる
        self.bracketStart=0#括弧の開始地点ではこれが1になる
        self.bracketStop=0#括弧の終了地点ではこれが1になる
        self.isNull=1#これの中身がないならば1になる

        #コンストラクタに渡された記号や数値などを解析して分類し、上のパラメーターを設定していく。
        processed=0
        try:#まずはfloat型数値のときについて書く。
            if float(data):
                self.isNull=0
                self.isNumber=1
                self.number=float(data)
                self.text=data
                processed=1
        except Exception:
            pass
        try:#次にint型数値について書く。
            if int(data):
                self.isNull=0
                self.isNumber=1
                self.number=float(data)
                self.text=data
                processed=1
        except Exception:
            pass
        try:#次に加算、乗算の記号や括弧などのときについての処理を書く。また、減産、除算についての記号などは、後に書くように数値自体を-にする、あとで(-1)をかける、逆数にする、などで処理を行う。
            if data=="+":
                self.isCommand=1
                self.isNull=0
                self.text=data
                processed=1
            if data=="*":
                self.isCommand=1
                self.isNull=0
                self.text=data
                processed=1
            if data=="(":
                self.isNull=0
                self.bracketStart=1
                processed=1
            if data==")":
                self.isNull=0
                self.bracketStop=1
                processed=1
        except Exception:
            pass
        if processed==0:
            print("式の形が不正です。")
            raise Exception()

class Tokenizer:
    #上で定義したToken型の変数について、普通の数式には複数あるので、まとめて扱いやすくするためのクラスを作る。
    def __init__(self,formula_raw):#formula_rawは文字列型の状態の数式
        self.data=[]#Token型の配列をここに代入していく
        self.bracketDepth=[]#ここにint型の配列という形で、式の括弧の構造に関する情報を入れていく。
        #入力された式が本当に正しいかテストする必要がある。
        #この下２行の変数を用いて、括弧の開始と終了の数が等しいか確認する。
        bracketStartNumber=0
        bracketStopNumber=0