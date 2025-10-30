from flask import Flask
from flask import request            #브라우저의 요청을 처리하기 위한 클래스
from flask import render_template    #페이지 렌더링을 위한 함수
from flask_pymongo import PyMongo
from flask import redirect
from bson.objectid import ObjectId 
from flask import flash



app = Flask(__name__)    #플라스크 객체(서버) 생성

app.config["SECRET_KEY"] = "abcd"
app.config["MONGO_URI"] = "mongodb+srv://admin:1234@cluster0.k9kk4ni.mongodb.net/mweb?"
mongo = PyMongo(app)     #mongo 변수를 통해 DB(myweb)에 접근 가능


@app.route("/")
def index(): 
    board = mongo.db.board
    datas = board.find()      # DB에서 모든 글 가져오기
    return render_template("index.html", datas=datas)


@app.route("/write", methods=["GET", "POST"])    #요청 방식에 따른 서로 다른 응답 구현
def write():
    if request.method == "POST":
        writer = request.form["writer"]
        password = request.form["password"]
        title = request.form["title"]
        contents = request.form["contents"]     #폼의 name 속성값이 contents인 데이터
        post = { "contents" : contents,"title" : title,"password" : password,"writer" : writer, }     #데이리)
        
        board = mongo.db.board     #board는 컬렉션(테이블)의 이름
        x = board.insert_one(post)
        return redirect( "/" )   # 몽고DB에 저장된 데이터의 _id 필드값(유일함)을 가져올 수 있음
    else:      #같은 경로(/write)에 대한 GET 요청(브라우저에서 주소 입력)에서의 응답 처리
        return render_template("write.html")  
    
@app.route("/view/<idx>")    # 팬시(간편, clean) URL 형식
def view(idx): 
    board = mongo.db.board
    data = board.find_one({"_id":ObjectId(idx)})  # DB에서 해당 게시물 가져오기
    return render_template("view.html", data=data)


@app.route("/delete/<idx>", methods=["GET", "POST"] )
def delete(idx):
    board = mongo.db.board
    data = board.find_one({"_id":ObjectId(idx)})   # 삭제할 데이터 가져오기
    if request.method == "POST":     # POST 요청(폼의 확인 클릭)에서의 응답 처리
        if request.form['password'] == data['password'] : # 패스워드 일치 확인
            board.delete_one({"_id":ObjectId(idx)})
            flash("삭제되었습니다")        
            return redirect("/") 
        else :
            flash("비밀번호가 올바르지 않습니다.")# 패스워드가 틀렸을 때
            return redirect("/delete/"+idx)
    else:      # 같은 경로 GET 요청(삭제 버튼 클릭)에서의 응답 처리
        return render_template("delete.html", data=data)



if __name__ == "__main__":    #파이썬의 엔트리 포인트(직접 실행된 파일에서만 True)
    app.run()    #플라스크 서버 실행