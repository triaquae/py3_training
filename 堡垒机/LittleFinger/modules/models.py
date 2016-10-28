#_*_coding:utf-8_*_
__author__ = 'Alex Li'


from sqlalchemy import create_engine,Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey,UniqueConstraint,UnicodeText,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import or_,and_
from sqlalchemy import func
from sqlalchemy_utils import ChoiceType,PasswordType


Base = declarative_base() #生成一个ORM 基类




BindHost2Group = Table('bindhost_2_group',Base.metadata,
    Column('bindhost_id',ForeignKey('bind_host.id'),primary_key=True),
    Column('group_id',ForeignKey('group.id'),primary_key=True),
)

BindHost2UserProfile = Table('bindhost_2_userprofile',Base.metadata,
    Column('bindhost_id',ForeignKey('bind_host.id'),primary_key=True),
    Column('uerprofile_id',ForeignKey('user_profile.id'),primary_key=True),
)

Group2UserProfile = Table('group_2_userprofile',Base.metadata,
    Column('userprofile_id',ForeignKey('user_profile.id'),primary_key=True),
    Column('group_id',ForeignKey('group.id'),primary_key=True),
)


class UserProfile(Base):
    __tablename__ = 'user_profile'
    id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(32),unique=True,nullable=False)
    password = Column(String(128),unique=True,nullable=False)
    groups = relationship('Group',secondary=Group2UserProfile)
    bind_hosts = relationship('BindHost',secondary=BindHost2UserProfile)
    audit_logs = relationship('AuditLog')

    def __repr__(self):
        return "<UserProfile(id='%s',username='%s')>" % (self.id,self.username)

class RemoteUser(Base):
    __tablename__ = 'remote_user'
    AuthTypes = [
        (u'ssh-passwd',u'SSH/Password'),
        (u'ssh-key',u'SSH/KEY'),
    ]
    id = Column(Integer,primary_key=True,autoincrement=True)
    auth_type = Column(ChoiceType(AuthTypes))
    username = Column(String(64),nullable=False)
    password = Column(String(255))

    __table_args__ = (UniqueConstraint('auth_type', 'username','password', name='_user_passwd_uc'),)

    def __repr__(self):
        return "<RemoteUser(id='%s',auth_type='%s',user='%s')>" % (self.id,self.auth_type,self.username)


class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer,primary_key=True,autoincrement=True)
    hostname = Column(String(64),unique=True,nullable=False)
    ip_addr = Column(String(128),unique=True,nullable=False)
    port = Column(Integer,default=22)
    #bind_hosts = relationship("BindHost")
    def __repr__(self):
        return "<Host(id='%s',hostname='%s')>" % (self.id,self.hostname)

class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer,primary_key=True)
    name = Column(String(64),nullable=False,unique=True)
    bind_hosts = relationship("BindHost",secondary=BindHost2Group, back_populates='groups' )
    user_profiles = relationship("UserProfile",secondary=Group2UserProfile )

    def __repr__(self):
        return "<HostGroup(id='%s',name='%s')>" % (self.id,self.name)


class BindHost(Base):
    '''Bind host with different remote user,
       eg. 192.168.1.1 mysql passAbc123
       eg. 10.5.1.6    mysql pass532Dr!
       eg. 10.5.1.8    mysql pass532Dr!
       eg. 192.168.1.1 root
    '''
    __tablename__ = 'bind_host'
    id = Column(Integer,primary_key=True,autoincrement=True)
    host_id = Column(Integer,ForeignKey('host.id'))
    remoteuser_id = Column(Integer,ForeignKey('remote_user.id'))

    host = relationship("Host")
    remoteuser = relationship("RemoteUser")
    groups = relationship("Group",secondary=BindHost2Group,back_populates='bind_hosts')
    #user_profiles = relationship("UserProfile",secondary=BindHost2UserProfile)
    audit_logs = relationship('AuditLog')

    __table_args__ = (UniqueConstraint('host_id', 'remoteuser_id', name='_bindhost_and_user_uc'),)

    def __repr__(self):
        return "<BindHost(id='%s',name='%s',user='%s')>" % (self.id,
                                                           self.host.hostname,
                                                           self.remoteuser.username
                                                                      )

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('user_profile.id'))
    bind_host_id = Column(Integer,ForeignKey('bind_host.id'))
    action_choices = [
        (0,'CMD'),
        (1,'Login'),
        (2,'Logout'),
        (3,'GetFile'),
        (4,'SendFile'),
        (5,'Exception'),
    ]
    action_choices2 = [
        (u'cmd',u'CMD'),
        (u'login',u'Login'),
        (u'logout',u'Logout'),
        #(3,'GetFile'),
        #(4,'SendFile'),
        #(5,'Exception'),
    ]
    action_type = Column(ChoiceType(action_choices2))
    #action_type = Column(String(64))
    cmd = Column(String(255))
    date = Column(DateTime)

    user_profile = relationship("UserProfile")
    bind_host = relationship("BindHost")
    '''def __repr__(self):
        return "<user=%s,host=%s,action=%s,cmd=%s,date=%s>" %(self.user_profile.username,
                                                      self.bind_host.host.hostname,
                                                              self.action_type,
                                                              self.date)
    '''
'''
class AuditLog(models.Model):
    session = models.ForeignKey(SessionTrack)
    user = models.ForeignKey('UserProfile')
    host = models.ForeignKey('BindHosts')
    action_choices = (
        (0,'CMD'),
        (1,'Login'),
        (2,'Logout'),
        (3,'GetFile'),
        (4,'SendFile'),
        (5,'exception'),
    )
    action_type = models.IntegerField(choices=action_choices,default=0)
    cmd = models.TextField()
    memo = models.CharField(max_length=128,blank=True,null=True)
    date = models.DateTimeField()


    def __unicode__(self):
        return '%s-->%s@%s:%s' %(self.user.user.username,self.host.host_user.username,self.host.host.ip_addr,self.cmd)
    class Meta:
        verbose_name = u'审计日志'
        verbose_name_plural = u'审计日志'

'''

if __name__ == '__main__':
    #SessionCls = sessionmaker(bind=engine) #创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
    #session = SessionCls()
    #h1 = session.query(Host).filter(Host.hostname=='ubuntu4').first()
    #hg1 = session.query(HostGroup).filter(HostGroup.name=='t2').first()

    #h2 = Host(hostname='ubuntu4',ip_addr='192.168.1.21')
    #h3 = Host(hostname='ubuntu5',ip_addr='192.168.1.24',port=20000)
    #hg= HostGroup(name='TestServers3',host_id=h3.id)
    #hg2= HostGroup(name='TestServers2',host_id=h2.id)
    #hg3= HostGroup(name='TestServers3')
    #hg4= HostGroup(name='TestServers4')
    #session.add_all([hg3,hg4])
    #h2.host_groups = [HostGroup(name="t1"),HostGroup(name="t2")]
    #h3.host_groups = [HostGroup(name="t2")]
    #h1.host_groups.append(HostGroup(name="t3") )
    #print(h1.host_groups)
    #print("hg1:",hg1.host.hostname)
    #join_res = session.query(Host).join(Host.host_groups).filter(HostGroup.name=='t1').group_by("Host").all()
    #print('join select:',join_res)
    #group_by_res = session.query(HostGroup, func.count(HostGroup.name )).group_by(HostGroup.name).all()
    #print("-------------group by res-----")

    '''
    h1=Host(hostname='h1',ip_addr='1.1.1.1')
    h2=Host(hostname='h2',ip_addr='1.1.1.2')
    h3=Host(hostname='h3',ip_addr='1.1.1.3')
    r1=RemoteUser(auth_type=u'ssh-passwd',username='alex',password='abc123')
    r2=RemoteUser(auth_type=u'ssh-key',username='alex')

    g1 = Group(name='g1')
    g2 = Group(name='g2')
    g3 = Group(name='g3')
    session.add_all([h1,h2,h3,r1,r2])
    session.add_all([g1,g2,g3])



    b1 = BindHost(host_id=1,remoteuser_id=1)
    b2 = BindHost(host_id=1,remoteuser_id=2)
    b3 = BindHost(host_id=2,remoteuser_id=2)
    b4 = BindHost(host_id=3,remoteuser_id=2)
    session.add_all((b1,b2,b3,b4))

    all_groups = session.query(Group).filter().all() #first()
    all_bindhosts = session.query(BindHost).filter().all()

    #h1 = session.query(BindHost).filter(BindHost.host_id==1).first()
    #h1.groups.append(all_groups[1])
    #print("h1:",h1)
    #print("----------->",all_groups.name,all_groups.bind_hosts)
    u1 = session.query(UserProfile).filter(UserProfile.id==1).first()
    print('--user:',u1.bind_hosts)
    print('--user:',u1.groups[0].bind_hosts)
    #u1.groups = [all_groups[1] ]
    #u1.bind_hosts.append(all_bindhosts[1])
    #u1 = UserProfile(username='alex',password='123')
    #u2 = UserProfile(username='rain',password='abc!23')
    #session.add_all([u1,u2])
    #b1 = BindHost()
    session.commit()
    #print(h2.host_groups)
    '''

