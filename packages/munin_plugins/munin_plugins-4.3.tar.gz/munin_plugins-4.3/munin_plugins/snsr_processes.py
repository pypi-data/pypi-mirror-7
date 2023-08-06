#!/usr/bin/python2.7

import os
import psutil
import re
from collections import deque

from .plugin import Plugin

from .utils import CachePickle
from .utils import CacheDict

from .env import SYSTEM_VALUE_CACHE
from .env import INSTANCES_CACHE

PROCESSES={
  'plone':True,
  'jboss':True,
  'catalina':True,
  }

SYSTEM_DEFAULTS=['cpu_times','virtual_memory','swap_memory','net_io_counters']

class Processes(Plugin):
  _title='Processes'
  _group='processes'
  _defaults={'minutes':5,
             'enabled':'cpu_usage_snsr,memory_snsr,connections_snsr,swap_snsr,storages_snsr,io_counters_snsr,io_counters_abs_snsr,threads_snsr',
            } 
  
  def install(self,plugins_dir,plug_config_dir):
    ans,def_create=self.ask('snsr_processes',plugins_dir)
    if (len(ans)==0 and def_create) or \
      (len(ans)>0 and ans.lower()=='y'):
      envvars=self._defaults.copy()
      for k,v in PROCESSES.items():
        envvars['process_%s'%k]=v      
      self.install_plugin('snsr_processes',plugins_dir,plug_config_dir,extended=dict(timeout=120),env=envvars)      
      
  def main(self,argv=None, **kw):     
    is_config=self.check_config(argv)
    title=self._title
    group=self._group

    printer=self.print_data
    if is_config:
      printer=self.print_config

    sys_prev,sys_curr=self.load_sys(SYSTEM_DEFAULTS)  
    ps_cache=self.load_process()
    
    analyzer_classes=[]
    
    for name in self.getenv('enabled').split(','):
      try:
        analyzer_classes.append(getattr(__import__("processes_analyzers",globals(),locals(),[name],-1),name))
      except (KeyError,ImportError) as e:        
        pass
    
    for cl in analyzer_classes:
      sensor=cl(sys_prev,sys_curr)

      print "multigraph processes_%s"%cl.__name__
      if is_config:
        print "graph_title %s %s"%(title,sensor.label)    
        print "graph_args --base 1000"
        print "graph_vlabel %s"%sensor.label
        print "graph_category %s"%group
      
      graph=sensor.graphType()
      for name,pd in ps_cache.items():  
        ids="%s_%s"%(name,cl.__name__)
        curr_value=getattr(pd,sensor.proc_mtd,lambda : None)()    
        
        res=sensor.calculate(name,curr_value)

        if isinstance(res,int) or isinstance(res,float):
          printer(id=ids,
                  value=res,
                  label=name,
                  draw=graph)
        elif isinstance(res,list) or isinstance(res,deque) or isinstance(res,set):
          for fd,row in res:
            printer(id='%s-%s'%(ids,fd),
                    value=row,
                    label='%s %s '%(name,fd),
                    draw=graph)        
      if not is_config:        
        sensor.store_in_cache()

    if not is_config:    
      #align prev with curr
      for k,v in sys_curr.items():    
        sys_prev[k]=v
      #store in the file
      sys_prev.store_in_cache()
      ps_cache.store_in_cache();

  def load_sys(self,defaults):
    cpath,ctype=SYSTEM_VALUE_CACHE

    #Fetch from cache
    try:
      cclass=eval(ctype)
      system_cache=cclass(cpath)
    except NameError:
      system_cache=None
    sys_curr={}
    
    for k in defaults:      
      sys_curr[k]=self.namedtuple2dict(getattr(psutil,k,lambda : None)())
      try:
        system_cache[k]
      except KeyError:  
        system_cache[k]=sys_curr[k]
    return system_cache,sys_curr
  
  def find_cfg(self,command):
    cfg=None
    for i in command:
      if 'zope.conf' in i or 'zeo.conf' in i:
        cfg=i     
    return cfg

  def build_sensor_name_plone(self,command):
    cfg=self.find_cfg(command)
    name=None
    if cfg is not None:
      try:
        instance=re.search('parts/(.*?)/etc',cfg).group(1)
        buildout=re.search('/(.*?)/parts',cfg).group(1)
      except AttributeError:
        pass
      else:
        path=buildout.split('/')
        name=path[-1]
        if name=='buildout':
          name=path[-2]
        name='%s_%s'%(name,instance)        
    return name

  def build_sensor_name_jboss(self,command):
    name=None
    plain=" ".join(command)
    if 'bin/java' in plain and 'org.jboss.Main' in plain:
        name='org.jboss.Main'    
    return name

  def build_sensor_name_catalina(self,command):
    name=None
    plain=" ".join(command)
    if 'bin/java' in plain and 'Bootstrap' in plain:
        name='catalina.startup.Bootstrap'    
    return name

  def build_sensor_name(self,command):
    name=None
    
    if self.getenv('process_plone'):
      name=self.build_sensor_name_plone(command)
      
    if self.getenv('process_jboss') and name is None:
      name=self.build_sensor_name_jboss(command)
      
    if self.getenv('process_catalina') and name is None:
      name=self.build_sensor_name_catalina(command)
      
    if name is not None:
      name=name.replace(".","_")
    
    return name

  def load_process(self):
    cache=CacheDict(INSTANCES_CACHE,def_value=None)
    for pd in psutil.process_iter(): 
      name=self.build_sensor_name(pd.cmdline())
      #ppid>1 means that is a child: this check is useful for zeo process 
      if name is not None and pd.ppid>1:
        cache[name]=pd
    return cache

def main(argv=None,**kw):
  Processes().main()
        
if __name__ == '__main__':
  main()

