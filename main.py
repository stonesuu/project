#!/bin/env python2.7
#coding=utf-8
from flask import Flask,session,request,render_template,redirect,json
import dbutil,time
conn = dbutil.DB('spare_parts','127.0.0.1','root','123456')
conn.connect()
SN_dict = {}
date_list = []
app = Flask(__name__)

def SN_dict_get(date):
	date_list.append(date)
	sn_get_sql = 'select SN from add_ where date_format(date,'+'"%Y-%m-%d")='
	sn_get_sql += '"%s"' % (date)
	sn_get_tuple = conn.execute(sn_get_sql)
	#print sn_get_sql
	#print '001',sn_get_tuple
	if len(sn_get_tuple) == 0:
		pass
	else:
		#print tuple(set(sn_get_tuple))
		for tmp_SN in tuple(set(sn_get_tuple)):
			tmp_SN_str = tmp_SN[0].encode('utf8')
			SN_key = tmp_SN_str[:-3]
			SN_val = int(tmp_SN_str[-3:].lstrip('0'))
			SN_dict.setdefault(SN_key,[]).append(SN_val)

#date_format = '%Y-%m-%d'
#date = time.strftime(date_format,time.localtime())
#SN_dict = SN_dict_get()


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

def getSN(big_class,small_class,location,date):#由于入库时间可选，那么对选择的入库时间要查询那一天的入库序列号，防止出现重复的现象。
	big_class_sql = 'select num from big_class where name="%s"' % (big_class)
	small_class_sql = 'select num from %s where name="%s"' % (change(big_class),small_class)
	location_sql = 'select num from location where name="%s"' % (location)
	big_class_num = conn.execute(big_class_sql)
	small_class_num = conn.execute(small_class_sql)
	location_num = conn.execute(location_sql)
	date = str(date.decode('utf8'))#每次入库时，需要根据时间查看内存中是否已经有那一天的序列字典，外部将内存中序列字典的日期写成了list。
	#print date
	#print type(date)
	tmp_str = [str(big_class_num[0][0]),str(small_class_num[0][0]),str(location_num[0][0])] + date.split('-')
	SN_ = ''.join(tmp_str)#序列号的前缀
	if date not in date_list:#查看插入的日期是否在list中，如果在list中，说明列表中存在那一天的序列字典
		SN_dict_get(date)
	if SN_ in SN_dict:#在序列字典中，序列前缀后面的list中是数字，如果要组成SN需要转换str并rjust操作后合并，序列的好处是求最大值，然后+1就是需要的新值
		last_num = max(SN_dict[SN_])#list中如果不是数字，而是处理过后的三位字符‘001’，那么由于在SN_dict_get之后list中的顺序是无法保持的，所以用SN_dict[SN_][-1],不一定
		new_num = last_num + 1      #是最大值，结果就错了三引号中就是原来的思路，结果导致重启程序后，某个list是['002','001'],然后产生新的值还是'002'
		SN_dict[SN_].append(new_num)
		SN = ''.join([SN_,str(new_num).rjust(3,'0')])
	else:
		SN_dict[SN_] = [1]
		SN = ''.join([SN_,str(1).rjust(3,'0')])
		'''
	if SN_ in SN_dict:
		last_num = int(SN_dict[SN_][-1].lstrip('0'))
		new_num = str(last_num + 1).rjust(3,'0')
		SN_dict[SN_].append(new_num)
		SN = ''.join([SN_,new_num])
		print 'old and SN_ in dict'
		print SN_dict
		print SN
	else:
		SN_dict[SN_] = ['001']
		SN = ''.join([SN_,'001'])
		print 'old and SN_ not in dict'
		print SN_dict
		print SN
	'''
	return (SN,u'入库',location,big_class,small_class,date)

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
	return render_template('/table.html')

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
		sql = 'select SN,location,big_class,small_class,date_format(date,"%Y-%m-%d")from add_'
		tmp = conn.execute(sql)
		res = json.dumps(tmp)
		#print res
		return res
	elif request.method == 'POST':
		big_class = request.form.get('big_class')
		small_class = request.form.get('small_class')
		location = request.form.get('location')
		date = request.form.get('date')
		SN_tuple = getSN(big_class,small_class,location,date)
		main_sql = 'insert into main_ (SN,status,big_class,small_class) values ("%s","%s","%s","%s")' % (SN_tuple[0],SN_tuple[1],SN_tuple[3],SN_tuple[4])
		add_sql = 'insert into add_ (SN,location,big_class,small_class,date) values ("%s","%s","%s","%s","%s")' % (SN_tuple[0],SN_tuple[2],SN_tuple[3],SN_tuple[4],SN_tuple[5])
		main_res = conn.execute(main_sql)
		add_res = conn.execute(add_sql)
		#print SN_dict
		if not (main_res and add_res):
			return SN_tuple[0]
		else:
			return 'error'

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
