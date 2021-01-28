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
        #場合によっては、処理をまとめて進めてあとで文字を一気に飛ばしたほうがいい場合が考えられるので、あえてiは数値としてループを回す。
        for i in range(0,len(formula_raw)):
            #まず、何も気にせず処理ができるのは(,)についてである。
            if formula_raw[i]=="(":
                self.data.append(Token("("))
                continue
            if formula_raw[i]==")":
                self.data.append(Token(")"))
                continue

            #次に、*や/について考える。
            #*や/の後ろに来うるものとして、数値や"+数値","-数値",(,-(のみが考えられる。もし+や-が来た場合は、その後ろの数値の符号として処理できる。（後述の理由で）
            #また、(-数値)という形の場合にも、"*-数値"のような形で扱って良い。(数式上"*-数値"は厳密には間違いではあるが、電卓である以上使いやすさや柔軟性があったほうがよく、
            #また"*-"という文字列については*(-数値)という意味にしかとれないため、このような設計にした。
            #まず掛け算について考える。
            if formula_raw[i]=="*":
                self.data.append(Token("*"))
                i+=1
                #上で数式の形式についてはチェックしたので、この場合はi+1が境界内かのチェックは不要
                if is_Int(formula_raw[i]) or formula_raw[i]=="+" or formula_raw[i]=="-":
                    cont=1
                    temp=""
                    while cont==1:
                        temp+=formula_raw[i]
                        if i==len(formula_raw)-1:
                            cont=0
                        i+=1
                    self.data.append(Token(temp))

        
test=Tokenizer("3*-33")
print("Hello!")