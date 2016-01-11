# main thread
import os
import string
import subprocess as sp
#io thread
from collections import deque
import threading

class PC:
	def __init__(self):
		self=self
	def __init__(self,name):
		self.name=name
		self.sn=name[1:]
	def get_name(self):
		return self.name
	def get_sn(self):
		return self.sn
	def get_ip(self):
		return self.ip
	def get_status(self):
		return self.status
	def get_user(self):
		return self.user
	def set_name(self,name):
		self.name=name
	def set_sn(self,sn):
		if sn==self.name:
			self.sn=self.name[1:]
		else:
			self.sn=sn
	def set_ip(self,ip):
		self.ip=ip
	def set_status(self,status):
		self.status=status
	def set_user(self,user):
		self.user=user
	def get_all(self):
		all = []
		all.append(self.name)
		all.append(self.sn)
		all.append(self.ip)
		all.append(self.status)
		all.append(self.user)
		return all

searching = 0
pc_queue = deque([])

def io_thread():
	t = threading.Thread(target=stack_listener)
	t.start()

def stack_listener():
	file_name='pc_network_info.csv'
	folder_name='script_output'
	try:
		os.mkdir(folder_name)
	except:
		print('Output folder already exists')
	output_folder=os.path.join(os.getcwd(),folder_name)

	all_titles=['Computername','Serialnumber',
		'IP Addr','Status','User']

	with open(os.path.join(output_folder,file_name),'w') as f:
 		f.write(";".join(all_titles)+'\n')
 		searching=1
		while(searching):
			if len(pc_queue)>0:
				l_out=";".join(pc_queue.popleft().get_all())
				f.write(l_out+'\n')
				print(l_out)
		f.close()
		return


def main_thread():
	pcs = []
	with open('pclist.csv') as pc_csv:
		for item in pc_csv:
			pcs.append(PC(item.strip())) # add string of name

	for pc in pcs:
		nfo=query_status_by_pc(pc.get_name())
		if nfo['status']=='Online':
			user=query_user_by_pc(pc.get_name())
		else:
			user=''
		pc.set_sn(pc.get_name())
		pc.set_ip(nfo['ip'])
		pc.set_status(nfo['status'])
		pc.set_user(user)
		pc_queue.append(pc)

	searching = 0

def query_status_by_pc(pcname):
	stat_dict = dict()
	try:
		ping_out=sp.check_output(['ping',pcname])
		if '[' in ping_out and ']' in ping_out:
			stat_dict['ip']=ping_out[string.find(ping_out,'[')+1
			:string.find(ping_out,']')]
		if 'Destination host unreachable' in ping_out:
			stat_dict['status']='Offline'
		elif 'time' in ping_out:
			stat_dict['status']='Online'
	except:
		stat_dict['ip']=''
		stat_dict['status']='Not in system'
	return stat_dict

def query_user_by_pc(pcname):
	user_list = []
	proc=sp.Popen(['psloggedon','\\\\'+pcname],shell=False,
		stdout=sp.PIPE, stderr=sp.PIPE)
	#ps_out=sp.check_output(['psloggedon','\\\\'+pcname])
	ps_out, ps_err = proc.communicate()
	print('OUT:'+ps_out)
	print('ERR:'+ps_err)
	for line in ps_out:
		if 'BAD\\' in line and not 'eRuntime' in line:
			user_list.append(line[string.find(line,'\\'):])
	if len(user_list)>1:
		return ",".join(user_list)
	elif len(user_list)==1:
		return user_list[0]
	else:
		return ''

if __name__ == "__main__":
	io_thread()
	main_thread() 
