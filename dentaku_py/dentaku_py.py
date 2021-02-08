Env_Colab=1#ファイル保存の方法を変えるために、Colab/jupyterの実行では1,PC上での実行では0にする

import math #sin,cos,tan,logなどの計算に使用するために使う
if Env_Colab:
    from google.colab import files

#引数として与えられたデータがInt型であるかどうかチェックして1か0を返す関数があると便利なので、定義する。
def is_Int(i):
    try:
        int(i)
        return 1
    except:
        return 0

#!!!ここから下の部分は、数式の処理と解釈を行う部分!!!#
#!!!ここから下の部分は、実際に数式を計算順序を考慮しながら四則演算について解くために使われる部分!!!
class Math_Token:
    #このクラスを利用して、数式から検出された、意味を持つ単語の最小単位である数値や加算減算などの記号、括弧などを使いやすい形で管理する。
    #このインスタンスの初期化に使える引数は計算に関する一部の記号と数値のみである。

    def __init__(self,data):#コンストラクタ
        self.isNumber=0#数値であるかどうかの情報、1or0
        self.text=""#データを文字で置いておく
        self.number=0.0#数値データの場合は数値に変わる
        self.isNull=1#これの中身がないならば1になる、これが1になった要素はデータを整える関数が呼び出されると同時に消される

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

        try:
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


class Math_Tokenizer:
    #上で定義したToken型の変数について、普通の数式には複数あるので、まとめて扱いやすくするためのクラスを作る。

    def __init__(self,formula_raw):#formula_rawは文字列型の状態の数式
        self.data=[]#Token型の配列をここに代入していく
        self.calcpoint=0#括弧の構造からどの部分を最初に計算すべきと言えるかの数値。data[calcpoint]は最も深い階層の最初の要素

        formula_raw=formula_raw.replace("--","+")

        #もし渡されたものが唯一つだけの数値であるならば、解析は必要ない。
        try:
            self.data.append(Math_Token(float(formula_raw)))
            return
        except:
            pass

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
        i=0
        while i<len(formula_raw):

            #まず、括弧については、２つ隣り合った場合は必要に応じて乗算記号を追加するように実装する。
            if formula_raw[i]=="(":
                self.data.append(Math_Token("("))
                i+=1
                continue
            if formula_raw[i]==")":
                self.data.append(Math_Token(")"))
                i+=1
                if i<len(formula_raw):
                    if formula_raw[i]=="(":
                        self.data.append(Math_Token("*"))
                continue

            #次に、*や/について考える。
            #*や/の後ろに来うるものとして、数値や"+数値","-数値",(,-(のみが考えられる。もし+や-が来た場合は、その後ろの数値の符号として処理できる。（後述の理由で）
            #また、(-数値)という形の場合にも、"*-数値"のような形で扱って良い。(数式上"*-数値"は厳密には間違いではあるが、電卓である以上使いやすさや柔軟性があったほうがよく、
            #また"*-"という文字列については*(-数値)という意味にしかとれないため、このような設計にした。）
            #まず掛け算について考える。
            #以下が"*数値","*+数値","*-数値"という形式についての実装である。
            if formula_raw[i]=="*":
                self.data.append(Math_Token("*"))
                i+=1
                #上で数式の形式についてはチェックしたので、この場合はi+1が境界内かのチェックは不要
                if is_Int(formula_raw[i]) or formula_raw[i]=="+" or formula_raw[i]=="-" or formula_raw[i]==".":
                    cont=1
                    temp=""
                    while cont==1:
                        temp+=formula_raw[i]
                        if i==len(formula_raw)-1:
                            cont=0
                        if cont:
                            if is_Int(formula_raw[i+1]):
                                pass
                            elif formula_raw[i+1]==".":
                                pass
                            else:
                                cont=0
                        i+=1
                    self.data.append(Math_Token(temp))
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
                            self.data.append(Math_Token(temp))
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
                    self.data.append(Math_Token("-1"))
                    self.data.append(Math_Token("*"))
                    self.data.append(Math_Token("("))
                    i+=2
                    continue
                if is_Int(formula_raw[i+1]) or formula_raw[i+1]==".":#後ろに数値が続く場合
                    cont=1
                    save=i
                    i+=1
                    temp="-"
                    while cont:
                        if i+1==len(formula_raw):
                            cont=0
                        if is_Int(formula_raw[i]) or formula_raw[i]==".":
                            temp+=formula_raw[i]
                        if i+1<len(formula_raw):
                            if is_Int(formula_raw[i+1]) == 0 and formula_raw[i+1]!=".":
                                cont=0
                        i+=1
                    if len(self.data)!=0:
                        if self.data[-1].isNumber:
                            self.data.append(Math_Token("+"))
                    self.data.append(Math_Token(temp))
                    continue

            #次に、ただの数値が存在している場合について考える。
            #この場合、前に述べたように、和の場合などは特段計算の指示をする記号については気にする必要はない。
            #前に")"が来ている場合、後ろに"("が来ている場合については、これは掛け算として扱う必要がある。
            if is_Int(formula_raw[i]):
                if i>0:#直前が括弧で終わっている場合、掛け算を挿入する処理
                    if formula_raw[i-1]==")":
                        self.data.append(Math_Token("*"))
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
                                continue
                        elif formula_raw[i]==".":#小数点である場合も上手く扱うためにこのようにしている
                            temp+=formula_raw[i]
                            i+=1
                            if i==len(formula_raw):
                                cont=0
                        elif formula_raw[i]=="(":
                            addMultiple=1#乗算記号の追加が必要かどうか判断する
                            cont=0
                        else:
                            cont=0
                    self.data.append(Math_Token(temp))
                    if addMultiple:#必要に応じて乗算記号を追加
                        self.data.append(Math_Token("*"))
                    continue
                else:
                    self.data.append(Math_Token(formula_raw[i]))
                    i+=1
                    continue

            #次に、i番目の文字が"+"である時のことを考える。
            #この場合の処理として、普通に"+"記号を追加すればいいだけである。
            if formula_raw[i]=="+":
                self.data.append(Math_Token("+"))
                i+=1
                continue

            #次に、i番目の文字が/である場合について考える。
            if formula_raw[i]=="/":
                self.data.append(Math_Token("/"))
                i+=1
                continue
        
        self.cleanup_unneeded_bracket()
        return


        
    def show_tokens(self):#現在保持している単語列を表示・列挙する
        string=""
        for i in self.data:
            string+=str(i.text)+" ; "
        print(string)

    def cleanup_null(self):#無視されていて消される予定の要素を消していく
        cp=[]
        for i in self.data:
            if i.isNull:
                pass
            else:
                cp.append(i)
        self.data=cp
            
    def cleanup_unneeded_bracket(self):#数値の両隣に括弧がある場合、その不要と言える括弧を消去する
        self.cleanup_null()
        for i in range(0,len(self.data)-2):
            if self.data[i].text=="(" and self.data[i+2].text==")":
                self.data[i].isNull=1
                self.data[i+2].isNull=1
        self.cleanup_null()

    def update_bracketinfo(self):#どこから計算し始めるのがいいか求めるために、括弧の構造について調べる。一番深い階層の始点の番号をself.calcpointに保持させる。
        self.cleanup_unneeded_bracket()
        i=0
        imax=0
        j=0
        self.calcpoint=0
        for k in self.data:
            if k.text=="(":
                i+=1
                if i>imax:
                    imax=i
                    self.calcpoint=j
            if k.text==")":
                i-=1
            j+=1

    def solve_onestep(self):#一ステップだけ計算を行う
        #計算を行わせるとき、まず、上の関数で求められた一番深い階層の中身について、*,/を探して演算する。
        #もしもない場合は、+について探して見つかれば演算を行う。
        #演算を行う記号の要素がそのまま演算結果の数値に変わる。
        #演算されてもう不要となった数値については、isNullが1になり、後でisNullとなっている要素を消すときに消えることになる。また、それまでの間、この要素は無視される。
        self.update_bracketinfo()#計算し始める場所の情報を更新する
        processing=self.calcpoint
        cont=1
        cont2adding=1
        while cont==1:#まず掛け算、割り算について処理する
            if self.data[processing].text==")" and cont:
                cont=0
                continue
            if self.data[processing].text=="*" and cont:
                self.data[processing]=Math_Token(self.data[processing-1].number*self.data[processing+1].number)
                self.data[processing-1].isNull=1
                self.data[processing+1].isNull=1
                cont=0
                cont2adding=0
            if self.data[processing].text=="/" and cont:
                self.data[processing]=Math_Token(self.data[processing-1].number/self.data[processing+1].number)
                self.data[processing-1].isNull=1
                self.data[processing+1].isNull=1
                cont=0
                cont2adding=0
            processing+=1
            if processing>=len(self.data)-1:
                cont=0
        #次に加算について処理する
        processing=self.calcpoint
        while cont2adding==1:
            if self.data[processing].text==")":
                cont2adding=0
                continue
            if self.data[processing].text=="+":
                self.data[processing]=Math_Token(self.data[processing-1].number+self.data[processing+1].number)
                self.data[processing-1].isNull=1
                self.data[processing+1].isNull=1
                cont2adding=0
            if processing>=len(self.data)-1:
                cont2adding=0
            processing+=1
        self.cleanup_unneeded_bracket()

    def solve(self):
        #この数式を完全に解く
        #要素の数は計算に伴い減っていき、最終的には答えの数値の要素のみが残る形となる。
        #そこで、なんども一ステップの演算と不要な要素の排除を繰り返し、要素が一つだけとなる状況を目指す。
        #残り要素が一つとなった時点で計算を終了し、結果が出たということにする。
        cont=1
        while cont==1:
            if len(self.data)==1:
                cont=0
                break
            elif len(self.data)==0:
                self.data.append(Math_Token("0"))
                break
            self.cleanup_unneeded_bracket()
            self.solve_onestep()


#!!!実際に四則演算の計算を解くために使われる部分はここまで!!!

#!!!ここから先は、数式を打ちやすくするための部分!!!
#数式を打ち込むときに、例えば途中に適宜スペースを加えても大丈夫な仕組みになっていると、見やすいように工夫して打ち込むことができるようになる。
#この電卓の機能である定数ショートカット機能もここで実装する。
def get_sanitized_input(string):
    return string.replace(" ","").replace("\R","8.3144626").replace("\G","9.80665").replace("\C","299792458").replace("\Z","*1.1")

#!!!ここから先については、この電卓の機能の一つである三角関数や対数関数の計算機能について実装していく。
#この部分については、実装を簡単にするためにあえて上の四則演算の計算とは切り離している。
#こうすることで、関数に渡された四則演算の式などを計算した上でsinなどの関数の結果を計算することが簡単になる。
#また、関数の括弧については、計算順序について示す括弧と区別するため、[]を使用することにする。
def function_solver(formula_raw):
    i=0#iについてはまだ処理できていない文字の場所を常に指すようにする。
    formula_output=""
    while i<len(formula_raw)-4:#式の後ろの部分について、関数(数値)がもし後ろに来ても少なくとも4文字は前に関数名が来ているはずなのでこれでよい
        if formula_raw[i] in "0123456789()+-*/.":#関数とは関係ない数式のとき
            formula_output+=formula_raw[i]
            i+=1
        elif formula_raw[i]=="[" or formula_raw[i]=="]":
            "関数名もなく括弧が入力されている状況なので入力ミス"
            raise Exception("数式の入力エラーがあります。関数の引数が存在しますが関数が存在しません。")
        elif formula_raw[i]=="S" and formula_raw[i+1]=="i" and formula_raw[i+2]=="n" and formula_raw[i+3]=="[":
            #この場合はこの関数はSin
            hikisuu=""
            cont=1
            i+=4
            try:
                while cont:
                    hikisuu+=formula_raw[i]
                    i+=1
                    if formula_raw[i]=="]":
                        i+=1
                        cont=0
            except:
                raise Exception("関数式の記述が不正です。")
            hikisuu=get_sanitized_input(hikisuu)
            solve=Math_Tokenizer(hikisuu)
            solve.solve()
            formula_output+=str(math.sin(float(solve.data[0].number)))

        elif formula_raw[i]=="C" and formula_raw[i+1]=="o" and formula_raw[i+2]=="s" and formula_raw[i+3]=="[":
            #この場合はこの関数はCos
            hikisuu=""
            cont=1
            i+=4
            try:
                while cont:
                    hikisuu+=formula_raw[i]
                    i+=1
                    if formula_raw[i]=="]":
                        i+=1
                        cont=0
            except:
                raise Exception("関数式の記述が不正です。")
            hikisuu=get_sanitized_input(hikisuu)
            solve=Math_Tokenizer(hikisuu)
            solve.solve()
            formula_output+=str(math.cos(float(solve.data[0].number)))

        elif formula_raw[i]=="T" and formula_raw[i+1]=="a" and formula_raw[i+2]=="n" and formula_raw[i+3]=="[":
            #この場合はこの関数はTan
            hikisuu=""
            cont=1
            i+=4
            try:
                while cont:
                    hikisuu+=formula_raw[i]
                    i+=1
                    if formula_raw[i]=="]":
                        i+=1
                        cont=0
            except:
                raise Exception("関数式の記述が不正です。")
            hikisuu=get_sanitized_input(hikisuu)
            solve=Math_Tokenizer(hikisuu)
            solve.solve()
            formula_output+=str(math.tan(float(solve.data[0].number)))

        
        elif formula_raw[i]=="L" and formula_raw[i+1]=="o" and formula_raw[i+2]=="g" and formula_raw[i+3]=="[":
            #この場合はこの関数はLog
            hikisuu=""
            cont=1
            i+=4
            try:
                while cont:
                    hikisuu+=formula_raw[i]
                    i+=1
                    if formula_raw[i]=="]":
                        i+=1
                        cont=0
            except:
                raise Exception("関数式の記述が不正です。")
            hikisuu=get_sanitized_input(hikisuu)
            solve=Math_Tokenizer(hikisuu)
            solve.solve()
            formula_output+=str(math.log(float(solve.data[0].number)))

        elif formula_raw[i]=="E" and formula_raw[i+1]=="x" and formula_raw[i+2]=="p" and formula_raw[i+3]=="[":
            #この場合はこの関数はExp
            hikisuu=""
            cont=1
            i+=4
            try:
                while cont:
                    hikisuu+=formula_raw[i]
                    i+=1
                    if formula_raw[i]=="]":
                        i+=1
                        cont=0
            except:
                raise Exception("関数式の記述が不正です。")
            hikisuu=get_sanitized_input(hikisuu)
            solve=Math_Tokenizer(hikisuu)
            solve.solve()
            formula_output+=str(math.exp(float(solve.data[0].number)))

        else:
            raise Exception("不正な文字が使用されています。")

    while i<len(formula_raw):
        formula_output+=formula_raw[i]
        i+=1
    return formula_output


def replace_val(form,Exec):#変数を計算前に実際の数値と置き換えるための関数
    for i in Exec.variable.keys():
        form=form.replace(str(i),str(Exec.variable[i]))
    return form

def evaluate_one_cond(input_string):
    if input_string=="1":
        return 1
    if input_string=="0":
        return 0
    if "<=" in input_string:
        try:
            temp=input_string.split("<=")
            if float(temp[0])<=float(temp[1]):
                return 1
            else:
                return 0
        except:
            raise Exception("条件式の値が不正です。")
    if "<" in input_string:
        try:
            temp=input_string.split("<")
            if float(temp[0])<float(temp[1]):
                return 1
            else:
                return 0
        except:
            raise Exception("条件式の値が不正です。")
    if ">" in input_string:
        try:
            temp=input_string.split(">")
            if float(temp[0])>float(temp[1]):
                return 1
            else:
                return 0
        except:
            raise Exception("条件式の値が不正です。")
    if ">=" in input_string:
        try:
            temp=input_string.split(">=")
            if float(temp[0])>=float(temp[1]):
                return 1
            else:
                return 0
        except:
            raise Exception("条件式の値が不正です。")
    if "==" in input_string:
        temp=input_string.split("==")
        if temp[0]==temp[1]:
            return 1
        try:
            if float(temp[0])==float(temp[1]):
                return 1
            else:
                return 0
        except:
            return 0
    return -1 #条件式が検出されない場合は-1を返す

def evaluate_cond(string_input,ExecInfo):
    #まずこれが条件式であるかどうか判断する必要がある。
    cond=1
    if "<=" in string_input or "<" in string_input or ">" in string_input or ">=" in string_input or "==" in string_input:
        pass
    else:
        return string_input
    #ここまでで、条件式ではないものはそのままreturnされている。
    #次に、このプログラムの変数を用いて、条件式の変数となっている部分を置き換えていく
    if len(ExecInfo.variable)!=0:
        for keys in ExecInfo.variable.keys():
            string_input=string_input.replace(str(keys),str(ExecInfo.variable[keys]))
    return evaluate_one_cond(string_input)

#ヘルプページを表示する関数
def helppage():
    print("簡単高機能電卓へようこそ！")
    print("")
    print("数式の入力方法について")
    print("数式には、数値、+-*/().およびSin[],Cos[],Tan[],Log[],Exp[]が使えます。")
    print("ただし、関数の引数として数式を使用することはできません。")
    print("")
    print("変数機能の使い方について")
    print("変数は、$(アルファベットの変数名)=(数値または数式)により代入できます。一度代入されると、$i=$i+1のような自身を使った計算もできます。")
    print("")
    print("FOR文、IF文の使い方について")
    print("FOR(条件式){指示;指示;指示......;指示},IF(条件式){指示;指示;指示;.....;指示}の形式で使えます。")
    print("条件式に使える記号は、==,<,>,<=,=>のみです。また、AND,OR計算には対応していません。")
    print("")
    print("スクリプト機能の使い方について")
    print("editorと入力すればスクリプトを記述できます。editor内ではsaveと入力すると保存して終了できます。")
    print("readと入力すればスクリプトなどのファイルを読み出して表示できます。")
    print("scriptと入力すればスクリプトを実行できます。")
    print("")
    print("定数ショートカット機能の使い方")
    print("数式中の文字の内、\Rは8.3144626（気体定数）に、\Gは9.80665に、\Cは299792458に変換されます。また、\Zと入力すると直前の数値が税込み数値に変換されます。")
    print("qを入力すればこのプログラムを終了できます。")

class ExecutionInfo:
    ExecutionOrder=""
    variable=dict()

#実際の計算などの指示の実行を行う関数
def ExecutionOneLine(ExecInfo):
    order=[]#ここに、実質行うべき命令たちを配列の形で収納する
    #FOR文についての処理を行う。
    for_continue=0
    execif=0
    execfor=0
    if ExecInfo.ExecutionOrder.startswith("FOR"):#for文の処理
        try:
            cond_cont=ExecInfo.ExecutionOrder.split("(")[1].split(")")[0]#計算を継続する条件を書く
            temp=ExecInfo.ExecutionOrder.split("{")[1].split("}")[0].split(";")#FOR文から、条件成立時に実行すべき命令の配列を取り出す
            order.append("CONT("+cond_cont+")")#FOR文の内容について、書き直した内部用記号で置き換える。
            #FOR文の場合だけfor_continueを1にして、もしこれが1ならばそのときだけはbreakされるまで複数回同じ命令を実行させる
            #成立時に実行する内容をorderに付け加える
            for i in temp:
                order.append(i)
            for_continue=1
            execfor=1
        except:
            raise Exception("条件式が不正です")
    #次にIF文について実装する。IF文もfor文と同じように、実行条件を内部向けの記号で置き換える。
    if ExecInfo.ExecutionOrder.startswith("IF"):
        try:
            cond_cont=ExecInfo.ExecutionOrder.split("(")[1].split(")")[0]#計算を継続する条件を書く
            temp=ExecInfo.ExecutionOrder.split("{")[1].split("}")[0].split(";")#IF文から、条件成立時に実行すべき命令の配列を取り出す
            temp.append("")
            order.append("CONT("+cond_cont+")")#IF文の内容について、書き直した内部用記号で置き換える。
            for i in temp:
                order.append(i)
                execif=1
        except:
            raise Exception("条件式が不正です")
    #FOR文でもIF文でもなかった場合の処理について書く
    if execfor==0 and execif==0:
        if ";" in ExecInfo.ExecutionOrder:
            for i in ExecInfo.ExecutionOrder.split(";"):
                order.append(i)
        else:
            order.append(ExecInfo.ExecutionOrder)
    #上で解釈した命令を実行していく
    cont_flag=1
    while cont_flag:
        cont_flag=for_continue
        for i in order:
            if i=="":
                continue
            if i.startswith("CONT("):
                cond_cont=evaluate_cond(i[5:len(i)-1],ExecInfo)
                if cond_cont==0:
                    cont_flag=0
                    break
                if cond_cont==1:
                    continue
            #ここから計算自体を行う
            if evaluate_cond(i,ExecInfo)==1:
                print(1)
                continue
            if evaluate_cond(i,ExecInfo)==0:
                print(0)
                continue
            substitute=0
            val=""
            if("=") in i:
                substitute=1
                temporar=i.split("=")
                val=temporar[0]
                i=temporar[1]
                if temporar[0].startswith("$"):
                    pass
                else:
                    raise Exception("変数名が不正です。")
            i=replace_val(i,ExecInfo)
            formula=function_solver(i)
            solveit=Math_Tokenizer(formula)
            solveit.solve()
            print(str(solveit.data[0].number))
            if substitute:
                ExecInfo.variable[val]=solveit.data[0].number

#ファイルの保存を行う関数
def write(filename,data):
    with open(filename,"w") as f:
        f.write(data)
        f.close()

#ファイルの読み出しを行う関数
def read(filename):
    tmp=""
    with open(filename,"r") as f:
        tmp=f.read()
        f.close()
    return tmp

#スクリプト編集モード
def editor():
    script=""
    while 1:
        temp=input("script>")
        if temp=="save":
            filename=input("filename?")
            write(filename,script)
            return
        script+=temp+"\n"

#スクリプト読み出しモード
def reader(arg):
    print(read(arg))

#スクリプト実行モード
def prgexec(filename,Exec):
    script=read(filename)
    script_tmp=script.split("\n")
    for i in script_tmp:
        if i=="":
            continue
        print(filename+">>>"+i)
        string_input=get_sanitized_input(i)
        Exec.ExecutionOrder=i
        ExecutionOneLine(Exec)

def shell():
    Exec=ExecutionInfo()
    while 1:
        try:
            string_input=get_sanitized_input(input(">>>"))
            if string_input=="script":#スクリプト実行
                filename=input("filename?")
                prgexec(filename,Exec)
                continue
            if string_input=="editor":#簡易的なエディタ起動
                editor()
                continue
            if string_input=="read":#ファイル読み出しモード
                reader(input("filename?"))
                continue
            if string_input=="q":
                return
            if string_input=="?" or string_input=="help":
                helppage()
                continue
            Exec.ExecutionOrder=string_input#実行する指示の内容についてインスタンスに書き込む
            ExecutionOneLine(Exec)#式を解釈し実行する
        except Exception as e:
            print(e)

#Mainloop
shell()