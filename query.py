# main thread
import os
import string
import subprocess as sp
import sys

class PC:
	def __init__(self,name,sn='',ip='',status='',user='',location=''):
		self.name=name
		self.sn=name[1:]
		self.ip=ip
		self.status=status
		self.user=user
		self.location=location
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
	def get_location(self):
		return self.location
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
	def set_location(self,location):
		self.location=location
	def get_all(self):
		all = []
		all.append(self.name)
		all.append(self.sn)
		all.append(self.ip)
		all.append(self.status)
		all.append(self.user)
		all.append(self.location)
		return all

class LocationMapper:
	def __init__(self,ip_addr):
		self.ip=ip_addr
		self.location_mapper=dict()
		with open('loclist.csv') as f:
			for l in f.readlines():
				map = l.split(';')
				self.location_mapper[map[0]]=map[1]
			f.close()
	def get_location(self):
		for key in self.location_mapper:
			if key in self.ip:
				return self.location_mapper[key].strip()

pc_queue = []

def main():
	all_titles=['Computername','Serialnumber',
		'IP Addr','Status','User','Location']
	pc_queue.append(";".join(all_titles)+'\n')
	
	file_name='pc_network_info.csv'
	folder_name='script_output'
	try:
		os.mkdir(folder_name)
	except:
		print('Output folder already exists')
	output_folder=os.path.join(os.getcwd(),folder_name)

	pcs = []

	with open(os.path.join(os.getcwd(),'pclist.csv'),'r') as pc_csv:
		for item in pc_csv:
			pcs.append(PC(item.strip())) # add string of name

	for pc in pcs:
		nfo=query_status_by_pc(pc.get_name())
		if nfo['status']=='Online':
			user=query_user_by_pc(pc.get_name())
			loc=LocationMapper(nfo['ip']).get_location()
		else:
			user=''
			loc=''
		pc.set_ip(nfo['ip'])
		pc.set_status(nfo['status'])
		pc.set_user(user)
		pc.set_location(loc)
		pcstring=";".join(pc.get_all())+'\n'
		pc_queue.append(pcstring)

	try:
		attempt_save(os.path.join(output_folder,file_name))
	except IOError:
		attempt_save(os.path.join(output_folder,'tmp_'+file_name))

	sys.exit()

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
	proc=sp.Popen(['psloggedon','\\\\'+pcname],shell=True,
		stdout=sp.PIPE, stderr=sp.PIPE)
	proc.wait()
	proc.wait()
	ps_out, ps_err = proc.communicate()
	for line in ps_out.split('\n'):
		if 'BAD' in line and not 'eRuntime' in line:
			username=line[string.find(line,'\\')+1:].strip('\n')
			print('User: '+username)
			user_list.append(username)
	if len(user_list)>1:
		return ",".join(user_list)[:-1]
	elif len(user_list)==1:
		return user_list[0][:-1]
	else:
		return ''

def attempt_save(fname,attempts=0):
	try:
		with open(fname,'w') as f:
	  		f.writelines(pc_queue)
	 		f.close()
	except IOError:
		if attempts>3:
			raise IOError('Permission denied')
		else:
			print('File could not be saved. Please check to make'
				+' sure that the file % is not open.', fname)
			time.sleep(5)
			attempt_save(fname,attempts+1)

if __name__ == "__main__":
	main() 
