#引数として与えられたデータがInt型であるかどうかチェックして1か0を返す関数があると便利なので、定義する。
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
        self.isNull=1#これの中身がないならば1になる、これが1になった要素はデータを整える関数が呼び出されると同時に消されて、

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

        try:#次に加算、乗算の記号や括弧などのときについての処理を書く。また、減算についての記号などは、後に書くように数値自体を-にする、あとで(-1)をかけるなどで処理を行う。
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
                self.text="("
                processed=1
            if data==")":
                self.isNull=0
                self.bracketStop=1
                self.text=")"
                processed=1
            if data=="/":
                self.isNull=0
                self.isCommand=1
                self.text=data
        except:
            pass


class Tokenizer:
    #上で定義したToken型の変数について、普通の数式には複数あるので、まとめて扱いやすくするためのクラスを作る。


    def __init__(self,formula_raw):#formula_rawは文字列型の状態の数式
        self.data=[]#Token型の配列をここに代入していく
        self.bracketDepth=[]#ここにint型の配列という形で、式の括弧により作られる構造に関する情報を入れていく。

        #せっかくここから構文を解析するので、見やすいように打ち込んでも大丈夫なように、数式の中に適宜スペースを入れても問題がないようにしたい。
        #入力された数式の中から全ての半角スペースを取り除けば良い。
        formula_raw=formula_raw.replace(" ","")

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
        i=0
        while i<len(formula_raw):




            #まず、括弧については、２つ隣り合った場合は必要に応じて乗算記号を追加するように実装する。
            if formula_raw[i]=="(":
                self.data.append(Token("("))
                i+=1
                continue
            if formula_raw[i]==")":
                self.data.append(Token(")"))
                i+=1
                if i<len(formula_raw):
                    if formula_raw[i]=="(":
                        self.data.append(Token("*"))
                continue

            #次に、*や/について考える。
            #*や/の後ろに来うるものとして、数値や"+数値","-数値",(,-(のみが考えられる。もし+や-が来た場合は、その後ろの数値の符号として処理できる。（後述の理由で）
            #また、(-数値)という形の場合にも、"*-数値"のような形で扱って良い。(数式上"*-数値"は厳密には間違いではあるが、電卓である以上使いやすさや柔軟性があったほうがよく、
            #また"*-"という文字列については*(-数値)という意味にしかとれないため、このような設計にした。）
            #まず掛け算について考える。
            #以下が"*数値","*+数値","*-数値"という形式についての実装である。
            if formula_raw[i]=="*":
                self.data.append(Token("*"))
                i+=1
                #上で数式の形式についてはチェックしたので、この場合はi+1が境界内かのチェックは不要
                if is_Int(formula_raw[i]) or formula_raw[i]=="+" or formula_raw[i]=="-" or formula_raw[i]==".":
                    cont=1
                    temp=""
                    while cont==1:
                        temp+=formula_raw[i]
                        if i==len(formula_raw)-1:
                            cont=0
                        if is_Int(formula_raw[i+1]):
                            pass
                        elif formula_raw[i+1]==".":
                            pass
                        else:
                            cont=0
                        i+=1
                        if i==len(formula_raw):
                            cont=0
                    self.data.append(Token(temp))
                    continue

                #つぎに、"*-(","*(-","*+(","*(+"という文字があった場合の処理について実装する。
                #これらの場合、括弧より先の部分に数値が一つあるか、２つあるかに応じて処理を変えるべきである。
                if formula_raw[i]+formula_raw[i+1] in ["-(","(-","+(","(+"]:
                    temp=""
                    if "-" in formula_raw[i]+formula_raw[i+1]:
                        temp="-"
                    save=i
                    i+=2
                    cont=1
                    while cont==1:
                        if i+1==len(formula_raw):
                            cont=0
                        if is_Int(formula_raw[i]):
                            temp+=formula_raw[i]
                        if formula_raw[i]==")":
                            self.data.append(Token(temp))
                            cont=0
                        if formula_raw[i] in "+-*/":
                            temp=""
                            i=save
                            cont=0
                        i+=1
                    continue
                continue

            #次に,-の場合について考える。
            #後ろに(が来ている場合は、*(-1)というふうに変換してやると処理できる。
            #後ろに数値が来ている場合は、その数値が負であるとして処理して良い。（後に、計算させる段階では、数値の要素が２つ隣り合った場合はそれらの和を取るようにする）
            if formula_raw[i]=="-":
                if formula_raw[i+1]=="(":#後ろに"("がある場合
                    self.data.append(Token("-1"))
                    self.data.append(Token("*"))
                    self.data.append(Token("("))
                    i+=2
                    continue
                if is_Int(formula_raw[i+1]):#後ろに数値が続く場合
                    cont=1
                    save=i
                    i+=1
                    temp="-"
                    while cont:
                        if i+1==len(formula_raw):
                            cont=0
                        if is_Int(formula_raw[i]):
                            temp+=formula_raw[i]
                        if is_Int(formula_raw[i+1]):
                            cont=0
                        i+=1
                    self.data.append(Token(temp))
                    continue

            #次に、ただの数値が存在している場合について考える。
            #この場合、前に述べたように、和の場合などは特段計算の指示をする記号については気にする必要はない。
            #前に")"が来ている場合、後ろに"("が来ている場合については、これは掛け算として扱う必要がある。
            if is_Int(formula_raw[i]):
                if i>0:#直前が括弧で終わっている場合、掛け算を挿入する処理
                    if formula_raw[i-1]==")":
                        self.data.append(Token("*"))
                #次に、どこまでが追加すべき数値であるかを分析して、数値の部分の文字列を取り出す。
                if i<len(formula_raw)-1:
                    temp=formula_raw[i]
                    cont=1
                    i+=1
                    addMultiple=0#これが1だった場合は乗算記号を追加する。
                    while cont:
                        if is_Int(formula_raw[i]):
                            temp+=formula_raw[i]
                            i+=1
                            if i==len(formula_raw):
                                cont=0
                        elif formula_raw[i]==".":#小数点である場合も上手く扱うためにこのようにしている
                            temp+=formula_raw[i]
                            i+=1
                            if i==len(formula_raw):
                                cont=0
                        elif formula_raw[i]=="(":
                            addMultiple=1#乗算記号の追加が必要かどうか判断する
                        else:
                            cont=0
                    self.data.append(Token(temp))
                    if addMultiple:#必要に応じて乗算記号を追加
                        self.data.append(Token("*"))
                    continue
                else:
                    self.data.append(Token(formula_raw[i]))
                    i+=1
                    continue

            #次に、i番目の文字が"+"である時のことを考える。
            #この場合の処理として、普通に"+"記号を追加すればいいだけである。
            if formula_raw[i]=="+":
                self.data.append(Token("+"))
                i+=1
                continue

            #次に、i番目の文字が/である場合について考える。
            if formula_raw[i]=="/":
                self.data.append(Token("/"))
                i+=1
                continue


    def show_tokens(self):#現在保持している単語列を表示・列挙する
        for i in self.data:
            print(i.text)

    def cleanup_null(self):#無視されていて消される予定の要素を消していく
        cp=self.data
        for i in self.data:
            if i.isNull:
                pass
            else:
                cp.append(i)
        data=cp
            





        
formula=input("数式を入力してください。")
solveit=Tokenizer(formula)
print("認識した数式はこちらです")
solveit.show_tokens()
