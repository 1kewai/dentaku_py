#Int型であるかどうかチェックする関数があると便利なので、定義する。
def is_Int(i):
    try:
        int(i)
        return 1
    except:
        return 0

class Token:
    #このクラスを利用して、数式から検出された、意味を持つ単語の最小単位である数値や加算減算などの記号、括弧などを使いやすい形で管理する。
    #このインスタンスの初期化に使える引数は計算に関する一部の記号と数値のみである。

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
        except:
            pass

        try:#次にint型数値について書く。
            if int(data):
                self.isNull=0
                self.isNumber=1
                self.number=float(data)
                self.text=data
                processed=1
        except:
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
        except:
            pass


class Tokenizer:
    #上で定義したToken型の変数について、普通の数式には複数あるので、まとめて扱いやすくするためのクラスを作る。


    def __init__(self,formula_raw):#formula_rawは文字列型の状態の数式
        self.data=[]#Token型の配列をここに代入していく
        self.bracketDepth=[]#ここにint型の配列という形で、式の括弧により作られる構造に関する情報を入れていく。

        #ここからのプログラムでは入力された数式のチェックを行う。

        #入力された式が本当に正しいかテストする必要がある。
        #括弧の開始と終了の数が等しいか確認する。
        bracketStartNumber=0
        bracketStopNumber=0
        for i in formula_raw:
            if i=="(":
                bracketStartNumber+=1
            if i==")":
                bracketStopNumber+=1
        if bracketStartNumber!=bracketStopNumber:
            raise Exception("括弧の始まる数と終わる数が合いません。数式が不正です。")

        #他に簡単にチェックできる事柄として、式の始まり方、終わり方が正しいかどうか、が挙げられる。
        #例えば、*や/から式が始まるのは入力間違いであるし、+や-,(で式が終わるのも入力間違いである。
        #これらはこの段階でチェックしておく。
        #式のはじめの文字について、許容できるのは数値、+,-,数値,(のいずれかである。
        CheckPattern="+-(0123456789"
        if formula_raw[0] in CheckPattern:
            pass
        else:
            raise Exception("不正な式です。")

        #式の終わりについては、許容できるのは数値、)のみである。
        OK=0
        CheckPattern=")0123456789"
        if formula_raw[-1] in CheckPattern:
            pass
        else:
            raise Exception("式の終わりに許容できない文字が使われています。")

        #次にこの式について、中身に不正な文字などが含まれていないことをチェックする必要がある。
        #数式の中にあってもよい文字として、数値、小数点、+,-,*,/,(,)が存在する。
        #それ以外が存在した場合は例外を上げる。
        OK=1
        error=0
        errorstr=""
        CheckPattern="0123456789+-*/()."
        for i in formula_raw:
            if i in CheckPattern:
                pass
            else:
                OK=0
                errorstr=i
        if OK==0:
            raise Exception("数式中に不正な文字が含まれています。確認して再試行してください。 at "+errorstr)

        #次にこの式について、考えられないパターンの文字列が存在しないかどうかをチェックする。
        #例えば、数式の中に(\や*)などの文字列が来たら不正であると言える。
        #このようなパターンは少ないので、実際に例を列挙してその中に当てはまるものがあるかを探すのが良さそうだ。
        DenyPattern=["(*","(/","+)","-)","*)","/)","()","+*","-*","+/","-/"]
        for i in DenyPattern:
            if i in formula_raw:
                raise Exception("数式に不正な記号の組み合わせが含まれています。 at "+i)
        #これで、数式の入力上のエラーについては全て対処できたことになる。
        #ここから、実際の数式の解析処理に入る。
        temp=""#数値などは複数の文字が連続しうるので、tempに一時的に文字を保存してまとめて処理することがある。
        
test=Tokenizer(")13(5/2)+3(")