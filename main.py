#!/bin/env python2.7
#coding=utf-8
from flask import Flask,session,request,render_template,redirect,json
import dbutil,time
conn = dbutil.DB('spare_parts','10.99.160.36','root','root')
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
	elif big_class == u'编码':
		return 'SN'
	elif big_class == u'位置':
		return 'location'
	elif big_class == u'大类':
		return 'big_class'
	elif big_class == u'细项':
		return 'small_class'
	elif big_class == u'日期':
		return 'date'
	elif big_class == u'使用日期':
		return 'date'
	elif big_class == u'维修日期':
		return 'date'
	elif big_class == u'报废日期':
		return 'date'
	elif big_class == u'使用位置':
		return 'where2use'
	elif big_class == u'维修厂商':
		return 'where2maint'

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

@app.route('/spare_parts/dash/get_add_sta')
def sp_d_gas():
	sql_get = 'select (select count(*) from add_ where big_class="%s" and used=0) as wangluo,' % (u'网络')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as fuwuqi,' % (u'服务器')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as zhongduan,' % (u'终端')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as tiebao,' % (u'铁包')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as tianche,' % (u'天车')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as guankong,' % (u'管控')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as jiankong,' % (u'监控')
	sql_get += '(select count(*) from add_ where big_class="%s" and used=0) as dianxin ' % (u'电信')
	sql_get += 'from dual'
	sql_use = 'select (select count(*) from use_ where big_class="%s") as wangluo,' % (u'网络')
	sql_use += '(select count(*) from use_ where big_class="%s") as fuwuqi,' % (u'服务器')
	sql_use += '(select count(*) from use_ where big_class="%s") as zhongduan,' % (u'终端')
	sql_use += '(select count(*) from use_ where big_class="%s") as tiebao,' % (u'铁包')
	sql_use += '(select count(*) from use_ where big_class="%s") as tianche,' % (u'天车')
	sql_use += '(select count(*) from use_ where big_class="%s") as guankong,' % (u'管控')
	sql_use += '(select count(*) from use_ where big_class="%s") as jiankong,' % (u'监控')
	sql_use += '(select count(*) from use_ where big_class="%s") as dianxin ' % (u'电信')
	sql_use += 'from dual'
	sql_maint = 'select (select count(*) from maintaince_ where big_class="%s") as wangluo,' % (u'网络')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as fuwuqi,' % (u'服务器')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as zhongduan,' % (u'终端')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as tiebao,' % (u'铁包')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as tianche,' % (u'天车')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as guankong,' % (u'管控')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as jiankong,' % (u'监控')
	sql_maint += '(select count(*) from maintaince_ where big_class="%s") as dianxin ' % (u'电信')
	sql_maint += 'from dual'
	sql_drop = 'select (select count(*) from drop_ where big_class="%s") as wangluo,' % (u'网络')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as fuwuqi,' % (u'服务器')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as zhongduan,' % (u'终端')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as tiebao,' % (u'铁包')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as tianche,' % (u'天车')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as guankong,' % (u'管控')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as jiankong,' % (u'监控')
	sql_drop += '(select count(*) from drop_ where big_class="%s") as dianxin ' % (u'电信')
	sql_drop += 'from dual'
	res_get = conn.execute(sql_get)
	res_use = conn.execute(sql_use)
	res_maint = conn.execute(sql_maint)
	res_drop = conn.execute(sql_drop)
	sta_dict = {'cata':[u'网络',u'服务器',u'终端',u'铁包',u'天车',u'管控',u'监控',u'电信'],'data_get':[],'data_use':[],'data_maint':[],'data_drop':[]}
	for num in res_get[0]:
		sta_dict['data_get'].append(int(num))
	for num in res_use[0]:
		sta_dict['data_use'].append(int(num))
	for num in res_maint[0]:
		sta_dict['data_maint'].append(int(num))
	for num in res_drop[0]:
		sta_dict['data_drop'].append(int(num))
	res = json.dumps(sta_dict)
	return res
	

@app.route('/spare_parts/add/get_page',methods=['GET'])
def sp_a_gp():
	return render_template('spare_parts_add.html')


@app.route('/spare_parts/add/get_table',methods=['GET','POST'])
def sp_a_gt():
	if request.method == 'GET':
		col = request.args.get('col')
		desc = request.args.get('desc')
		#print col,desc
		if col == None and desc == None:
			sql = 'select SN,location,big_class,small_class,date_format(date,"%Y-%m-%d")from add_ where used=0'
		else:
			if int(desc) == 0:
				#print 'up'
				sql = 'select SN,location,big_class,small_class,date_format(date,"%Y-%m-%d")'+'from add_ where used=0 order by %s' %(change(col),)
			else:
				#print 'down'
				sql = 'select SN,location,big_class,small_class,date_format(date,"%Y-%m-%d")'+'from add_ where used=0 order by %s desc' %(change(col),)
		#print sql			
		tmp = conn.execute(sql)
		res = json.dumps(tmp)
		return res
	elif request.method == 'POST':
		big_class = request.form.get('big_class')
		small_class = request.form.get('small_class')
		location = request.form.get('location')
		date = request.form.get('date')
		SN_tuple = getSN(big_class,small_class,location,date)
		main_sql = 'insert into main_ (SN,status,big_class,small_class,get_date) values ("%s","%s","%s","%s","%s")' % (SN_tuple[0],SN_tuple[1],SN_tuple[3],SN_tuple[4],SN_tuple[5])
		add_sql = 'insert into add_ (SN,location,big_class,small_class,date) values ("%s","%s","%s","%s","%s")' % (SN_tuple[0],SN_tuple[2],SN_tuple[3],SN_tuple[4],SN_tuple[5])
		main_res = conn.execute(main_sql)
		add_res = conn.execute(add_sql)
		#print SN_dict
		if not (main_res or add_res):
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

@app.route('/spare_parts/add/del_sn',methods=['POST'])
def sp_a_ds():
	sn = request.form.get('sn')
	main_sql = 'delete from main_ where SN="%s"' % (sn)
	add_sql = 'delete from add_ where SN="%s"' % (sn)
	main_res = conn.execute(main_sql)
	add_res = conn.execute(add_sql)
	if not (main_res or add_res):
		return 'ok'
	else:
		return 'error'

@app.route('/spare_parts/use/get_message',methods=['GET'])
def sp_u_gm():
	sn = request.args.get('sn')
	sql = 'select location,big_class,small_class,date_format(date,"%Y-%m-%d")'+'from add_ where SN="%s"' % (sn)
	res = getjson(sql)
	return res

@app.route('/spare_parts/use/get_table',methods=['GET','POST'])
def sp_u_gt():
	if request.method == 'GET':
		col = request.args.get('col')
		desc = request.args.get('desc')
		if col == None and desc == None:
			sql = 'select SN,big_class,small_class,where2use,date_format(date,"%Y-%m-%d") from use_'
		else:
			if int(desc) == 0:
				sql = 'select SN,big_class,small_class,where2use,date_format(date,"%Y-%m-%d") '+'from use_ order by %s' % (change(col),)
			else:
				sql = 'select SN,big_class,small_class,where2use,date_format(date,"%Y-%m-%d") '+'from use_ order by %s desc' % (change(col),)
		res = getjson(sql)
		#print res
		return res
	else:
		sn = request.form.get('sn')
		where2use = request.form.get('where2use')
		date = request.form.get('date')
		main_sql = 'update main_ set status="使用",use_date="%s" where SN="%s"' % (date,sn)
		add_sql = 'update add_ set used=1 where SN="%s"' % (sn)
		use_sql = 'insert into use_(SN,big_class,small_class,where2use,date) select SN,big_class,small_class,"%s","%s" from add_ where SN="%s"' % (where2use,date,sn)
		main_res = conn.execute(main_sql)
		add_res = conn.execute(add_sql)
		use_res = conn.execute(use_sql)
		if not (main_res or add_res or use_res):
			return 'ok'
		else:
			return 'error'

@app.route('/spare_parts/maintaince/get_message',methods=['GET'])
def sp_mt_gm():
	sn = request.args.get('sn')
	sql = 'select big_class,small_class,where2use,date_format(date,"%Y-%m-%d")'+'from use_ where SN="%s"' % (sn)
	res = getjson(sql)
	return res

@app.route('/spare_parts/maintaince/get_table',methods=['GET','POST'])
def sp_mt_gt():
	if request.method == 'GET':
		col = request.args.get('col')
		desc = request.args.get('desc')
		if col == None and desc == None:
			sql = 'select SN,big_class,small_class,where2maint,date_format(date,"%Y-%m-%d") from maintaince_'
		else:
			if int(desc) == 0:
				sql = 'select SN,big_class,small_class,where2maint,date_format(date,"%Y-%m-%d")'+' from maintaince_ order by %s' %(change(col),)
			else:
				sql = 'select SN,big_class,small_class,where2maint,date_format(date,"%Y-%m-%d")'+' from maintaince_ order by %s desc' %(change(col),)	
		res = getjson(sql)
		#print res
		return res
	else:
		sn = request.form.get('sn')
		where2maint = request.form.get('where2maint')
		date = request.form.get('date')
		main_sql = 'update main_ set status="维修",maint_date="%s" where SN="%s"' % (date,sn)
		maintaince_sql = 'insert into maintaince_(SN,big_class,small_class,where2maint,date) select SN,big_class,small_class,"%s","%s" from use_ where SN="%s"' % (where2maint,date,sn)
		use_sql = 'delete from use_ where SN="%s"' % (sn)	
		main_res = conn.execute(main_sql)
		maintaince_res = conn.execute(maintaince_sql)
		use_res = conn.execute(use_sql)
		#print '001',maintaince_res,'002',main_res,'003',use_res
		if not (maintaince_res or main_res or use_res):
			return 'ok'
		else:
			return 'error'
@app.route('/spare_parts/maintaince/reuse',methods=['POST'])
def sp_m_r():
	sn = request.form.get('sn')
	date = request.form.get('date')
	round_get_sql = 'select count(*) from round_ where SN="%s"' % (sn)
	round_get_res = conn.execute(round_get_sql)[0][0]
	round_sql = 'insert into round_(SN,big_class,small_class,get_date,use_date,maint_date,round) select SN,big_class,small_class,get_date,use_date,maint_date,"%s" from main_ where SN="%s"' % (round_get_res+1,sn)
	main_sql = 'update main_ set get_date="%s",use_date=null,maint_date=null where SN="%s"' % (date,sn)
	add_sql = 'update add_ set date="%s",used=0 where SN="%s"' % (date,sn)
	maintaince_sql = 'delete from maintaince_ where SN="%s"' % (sn)
	round_res = conn.execute(round_sql)
	main_res = conn.execute(main_sql)
	add_res = conn.execute(add_sql)
	maintaince_res = conn.execute(maintaince_sql)
	if not (round_res or main_res or add_res or maintaince_res):
		return 'ok'
	else:
		return 'error'
@app.route('/spare_parts/drop/get_message',methods=['GET','POST'])
def sp_d_gm():
	if request.method == 'POST':
		sn = request.form.get('sn')
		sql = 'select status from main_ where SN="%s"' % (sn)
		res_tuple = conn.execute(sql)
		res = res_tuple[0][0]
		if res == u'入库':
			return 'add'
		elif res == u'使用':
			return 'use'
		elif res == u'维修':
			return 'maint'
		else:
			return 'unknow'
	else:
		sn = request.args.get('sn')
		status = request.args.get('status')
		if status == 'add':
			sql = 'select location,big_class,small_class,date_format(date,"%Y-%m-%d")'+' from add_ where SN="%s"' % (sn)
			res = getjson(sql)
		elif status == 'use':
			sql = 'select big_class,small_class,where2use,date_format(date,"%Y-%m-%d")' + ' from use_ where SN="%s"' % (sn)
			res = getjson(sql)
		elif status == 'maint':
			sql = 'select big_class,small_class,where2maint,date_format(date,"%Y-%m-%d")'+' from maintaince_ where SN="%s"' % (sn)
			res = getjson(sql)
		return res

@app.route('/spare_parts/drop/get_table',methods=['GET','POST'])
def sp_d_gt():
	if request.method == 'GET':
		col = request.args.get('col')
		desc = request.args.get('desc')
		if col == None and desc == None:
			sql = 'select SN,big_class,small_class,date_format(date,"%Y-%m-%d") from drop_'
		else:
			if int(desc) == 0:
				sql = 'select SN,big_class,small_class,date_format(date,"%Y-%m-%d")'+' from drop_ order by %s' % (change(col),)
			else:
				sql = 'select SN,big_class,small_class,date_format(date,"%Y-%m-%d")'+' from drop_ order by %s desc' % (change(col),)
		res = getjson(sql)
		return res
	else:
		sn = request.form.get('sn')
		sn_from = request.form.get('sn_from')
		date = request.form.get('date')
		if sn_from == 'add':
			add_sql = 'update add_ set used=1 where SN="%s"' % (sn)
			main_sql = 'update main_ set status="报废",drop_date="%s" where SN="%s"' % (date,sn)
			drop_sql = 'insert into drop_(SN,big_class,small_class,date) select SN,big_class,small_class,"%s" from add_ where SN="%s"' % (date,sn)
			add_res = conn.execute(add_sql)
			main_res = conn.execute(main_sql)
			drop_res = conn.execute(drop_sql)
			if not (add_res or main_res or drop_res):
				return 'ok'
			else:
				return 'error'
		elif sn_from == 'use':
			drop_sql = 'insert into drop_(SN,big_class,small_class,date) select SN,big_class,small_class,"%s" from use_ where SN="%s"' % (date,sn)
			main_sql = 'update main_ set status="报废",drop_date="%s" where SN="%s"' % (date,sn)
			use_sql = 'delete from use_ where SN="%s"' % (sn)
			drop_res = conn.execute(drop_sql)
			main_res = conn.execute(main_sql)
			use_res = conn.execute(use_sql)
			if not (drop_res or main_res or use_res):
				return 'ok'
			else:
				return 'error'
		elif sn_from == 'maint':
			drop_sql = 'insert into drop_(SN,big_class,small_class,date) select SN,big_class,small_class,"%s" from maintaince_ where SN="%s"'  % (date,sn)
			main_sql = 'update main_ set status="报废",drop_date="%s" where SN="%s"' % (date,sn)
			maintaince_sql = 'delete from maintaince_ where SN="%s"' % (sn)
			drop_res = conn.execute(drop_sql)
			main_res = conn.execute(main_sql)
			maintaince_res = conn.execute(maintaince_sql)
			if not (drop_res or main_res or maintaince_res):
				return 'ok'
			else:
				return 'error'
		else:
			return 'unknow error'
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
	#print sql
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
@app.route('/test')
def test():
	res = {'cata':['001','002','003'],'data':[3,6,9]}
	resjson = json.dumps(res)
	return resjson


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=9023,debug=True)
