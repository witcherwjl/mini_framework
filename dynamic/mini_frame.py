import re
from pymysql import connect
import urllib.parse
import logging

"""
URL_FUNC_DICT = {
    "/index.html": index,
    "/center.html": center
}
"""

URL_FUNC_DICT = dict()


def route(url):
    def set_func(func):
        # URL_FUNC_DICT["/index.py"] = index
        URL_FUNC_DICT[url] = func
        def call_func(*args, **kwargs):
            return func(*args, **kwargs)
        return call_func
    return set_func

@route(r"/add/(\d+)\.html")
def add_focus(ret):

    stock_code = ret.group(1)

    conn = connect(host='127.0.0.1',port=3306,user='root',password='123',database='stock_db',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    sql = """select * from info where code=%s"""
    cs.execute(sql, (stock_code,))

    #若没有则返回
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有这个" 
    
    #若有则看是否关注过
    sql = """select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s;"""
    if cs.fetchone():
        cs.close()
        conn.close()
        return "已经有这个"

    sql = """insert into focus (info_id) select id from info where code=%s"""
    cs.execute(sql, (stock_code,))
    conn.commit()
    cs.close()
    conn.close()

    return "add ok.."

@route(r"/del/(\d+)\.html")
def del_focus(ret):

    stock_code = ret.group(1)

    conn = connect(host='127.0.0.1',port=3306,user='root',password='123',database='stock_db',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    sql = """select * from info where code=%s"""
    cs.execute(sql, (stock_code,))

    #若没有则返回
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有这个" 
    
    #若有则看是否关注过
    sql = """select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s;"""
    cs.execute(sql,(stock_code,))
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有关注国"
    #删除
    sql = """delete from focus where info_id=(select id from info where code=%s)"""
    cs.execute(sql, (stock_code,))
    conn.commit()
    cs.close()
    conn.close()

    return "delete ok.."


@route(r"/update/(\d+)\.html")
def show_update_page(ret):

    stock_code = ret.group(1)

    with open("./templates/update.html") as f:
        content = f.read()

    conn = connect(host='127.0.0.1',port=3306,user='root',password='123',database='stock_db',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    
    sql="""select f.note_info from focus as f inner join info as i on i.id=f.info_id where i.code=%s;"""
    cs.execute(sql, (stock_code,))
    stock_infos = cs.fetchone()
    note_info = stock_infos[0]
    
    cs.close()
    conn.close()
    
    content = re.sub(r"\{%note_info%\}", note_info, content)
    content = re.sub(r"\{%code%\}", stock_code, content)

    return content

@route(r"/update/(\d+)/(.*)\.html")
def save_update_page(ret):

    stock_code = ret.group(1)
    save_content = ret.group(2)
    save_content = urllib.parse.unquote(save_content)


    with open("./templates/update.html") as f:
        content = f.read()

    conn = connect(host='127.0.0.1',port=3306,user='root',password='123',database='stock_db',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    
    sql="""update focus set note_info=%s where info_id=(select id from info where code=%s);"""
    cs.execute(sql, (save_content, stock_code))
    conn.commit()
    cs.close()
    conn.close()

    return "修改成功"

@route(r"/index.html")
def index(ret):
    with open("./templates/index.html") as f:
        content = f.read()

    # my_stock_info = "哈哈哈哈 这是你的本月名称....."
    # content = re.sub(r"\{%content%\}", my_stock_info, content)
    # 创建Connection连接
    conn = connect(host='127.0.0.1',port=3306,user='root',password='123',database='stock_db',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    cs.execute("select * from info;")
    stock_infos = cs.fetchall()
    #print(stock_infos)
    cs.close()
    conn.close()

    tr_template = """<tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
        </td>
        </tr>
    """

    html = ""
    for line_info in stock_infos:
        html += tr_template % (line_info[0],line_info[1],line_info[2],line_info[3],line_info[4],line_info[5],line_info[6],line_info[7],line_info[1])
    #print(html)
    # content = re.sub(r"\{%content%\}", str(stock_infos), content)
    content = re.sub(r"\{%content%\}", html, content)

    return content
     

@route(r"/center.html")
def center(ret):
    with open("./templates/center.html") as f:
        content = f.read()

    # my_stock_info = "这里是从mysql查询出来的数据。。。"
    # content = re.sub(r"\{%content%\}", my_stock_info, content)
    # 创建Connection连接
    conn = connect(host='127.0.0.1',port=3306,user='root',password='123',database='stock_db',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    cs.execute("select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id=f.info_id;")
    stock_infos = cs.fetchall()
    cs.close()
    conn.close()

    tr_template = """
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
            </td>
        </tr>
    """

    html = ""
    for line_info in stock_infos:
        html += tr_template % (line_info[0],line_info[1],line_info[2],line_info[3],line_info[4],line_info[5],line_info[6],line_info[0], line_info[0])

    # content = re.sub(r"\{%content%\}", str(stock_infos), content)
    content = re.sub(r"\{%content%\}", html, content)

    return content


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    
    file_name = env['PATH_INFO']

    logging.basicConfig(level=logging.INFO,
                        filename='./log.txt',
                        filemode='a',
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    logging.info("访问的是，%s" % file_name)

    try:
        for url, func in URL_FUNC_DICT.items():
            ret = re.match(url, file_name)
            if ret:
                return func(ret)
        else:
            logging.warning("没有对应的函数....")
            return "请求的url(%s)没有对应的函数" % file_name
    except Exception as ret:
        return "产生了异常：%s" % str(ret)

