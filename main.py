#!/bin/env python2.7
#coding=utf-8
from flask import Flask,session,request,render_template,redirect,json
import dbutil
conn = dbutil.DB('spare_parts','10.1.1.7','root','root')
conn.connect()
app = Flask(__name__)


def getjson(sql):
	try:
		tmp = conn.execute(sql)
		res = json.dumps(tmp)
	except Exception as e:
		return 'error'
	else:
		return res

def change(big_class):
	if big_class == u'网络':
		return 'wangluo'
	elif big_class == u'服务器':
		return 'fuwuqi'
	elif big_class == u'终端':
		return 'zhongduan'
	elif big_class == u'铁包':
		return 'tiebao'
	elif big_class == u'天车':
		return 'tianche'
	elif big_class == u'管控':
		return 'guankong'
	elif big_class == u'监控':
		return 'jiankong'
	elif big_class == u'电信':
		return 'dianxin'

@app.route('/login',methods=['GET','POST'])
def login():
	if 'user' in session:
		return redirect('/main')
	else:
		sql = 'select username from user_management'
		
		if request.method == 'GET':
			return render_template('login.html')
		elif request.method == 'POST':
			user = request.form.get('user')
			passwd = request.form.get('passwd')
			sql = 'select '
@app.route('/')
def login_default():
	return redirect('/login')

@app.route('/spare_parts/main/get_page',methods=['GET','POST'])
def sp_m_gp():
	if request.method == 'GET':
		return render_template('spare_parts.html')

@app.route('/spare_parts/main/get_table')
def sp_m_gt():
	sql = 'select name,status,provider,price,network,server,terminal,tianche,tiebao,guankong,jiankong,dianxin from main_'
	tmp = conn.execute(sql)
	res = json.dumps(tmp)
	return res

@app.route('/spare_parts/add/get_page',methods=['GET'])
def sp_a_gp():
	return render_template('spare_parts_add.html')

@app.route('/spare_parts/add/get_table',methods=['GET','POST'])
def sp_a_gt():
	if request.method == 'GET':
		sql = 'select SN,name,location,time from add_'
		tmp = conn.execute(sql)
		res = json.dumps(tmp)
		return res
	elif request.method == 'POST':
		big_class = request.form.get('big_class')
		small_class = request.form.get('small_class')
		location = request.form.get('location')
		date = request.form.get('date')
		print big_class,small_class,location,date
		return 'ok'

@app.route('/spare_parts/add/get_big_class')
def sp_a_gbc():
	sql = 'select name from big_class'
	tmp = conn.execute(sql)
	res = json.dumps(tmp)
	return res

@app.route('/spare_parts/add/get_small_class')
def sp_a_gsc():
	big_class=request.args.get('big_class')
	sql = 'select name from %s' %(change(big_class))
	res = getjson(sql)
	return res

@app.route('/spare_parts/set/get_page')
def sp_s_gp():
	return render_template('spare_parts_set.html')

@app.route('/spare_parts/set/get_table')
def sp_s_gt():
	big_class=request.args.get('big_class')
	sql = 'select * from %s' % (change(big_class))
	res = getjson(sql)
	return res

@app.route('/spare_parts/set/add_small_class',methods=['POST'])
def sp_s_asc():
	big_class = request.form.get('big_class')
	small_class = request.form.get('small_class')
	sql = 'insert into %s(name) values ("%s")' % (change(big_class),small_class)
	print sql
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'
@app.route('/spare_parts/set/del_small_class',methods=['POST'])
def sp_s_dsc():
	big_class = request.form.get('big_class')
	data_id = request.form.get('data_id')
	sql = 'delete from %s where num=%s' % (change(big_class),data_id)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'

@app.route('/spare_parts/set/set_small_class',methods=['POST'])
def sp_s_ssc():
	big_class = request.form.get('big_class')
	data_id = request.form.get('data_id')
	data_content = request.form.get('data_content')
	sql = 'update %s set name="%s" where num=%s' % (change(big_class),data_content,data_id)
	res = conn.execute(sql)
	if not res:
		return 'ok'
	else:
		return 'error'


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=9023,debug=True)
