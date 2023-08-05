import datetime
from flask import g
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from flask.ext.appbuilder import Base
from .._compat import as_unicode


_dont_audit = False


class Permission(Base):
    __tablename__ = 'ab_permission'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ViewMenu(Base):
    __tablename__ = 'ab_view_menu'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) and (self.name == other.name)

    def __neq__(self, other):
        return self.name != other.name

    def __repr__(self):
        return self.name


class PermissionView(Base):
    __tablename__ = 'ab_permission_view'
    id = Column(Integer, primary_key=True)
    permission_id = Column(Integer, ForeignKey('ab_permission.id'))
    permission = relationship("Permission")
    view_menu_id = Column(Integer, ForeignKey('ab_view_menu.id'))
    view_menu = relationship("ViewMenu")

    def __repr__(self):
        return str(self.permission).replace('_', ' ') + ' on ' + str(self.view_menu)


assoc_permissionview_role = Table('ab_permission_view_role', Base.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('permission_view_id', Integer, ForeignKey('ab_permission_view.id')),
                                  Column('role_id', Integer, ForeignKey('ab_role.id'))
)


class Role(Base):
    __tablename__ = 'ab_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    permissions = relationship('PermissionView', secondary=assoc_permissionview_role, backref='role')

    def __repr__(self):
        return self.name


class User(Base):
    __tablename__ = 'ab_user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(256))
    active = Column(Boolean)
    email = Column(String(64), unique=True, nullable=False)

    last_login = Column(DateTime)
    login_count = Column(Integer)
    fail_login_count = Column(Integer)

    role_id = Column(Integer, ForeignKey('ab_role.id'), nullable=False)
    role = relationship("Role")

    created_on = Column(DateTime, default=datetime.datetime.now, nullable=True)

    changed_on = Column(DateTime, default=datetime.datetime.now, nullable=True)

    @declared_attr
    def created_by_fk(self):
        return Column(Integer, ForeignKey('ab_user.id'),
                      default=self.get_user_id, nullable=True)

    @declared_attr
    def changed_by_fk(self):
        return Column(Integer, ForeignKey('ab_user.id'),
                      default=self.get_user_id, nullable=True)

    created_by = relationship("User", backref=backref("created", uselist=True),
                              remote_side=[id], primaryjoin='User.created_by_fk == User.id', uselist=False)
    changed_by = relationship("User", backref=backref("changed", uselist=True),
                              remote_side=[id], primaryjoin='User.changed_by_fk == User.id', uselist=False)


    @classmethod
    def get_user_id(cls):
        try:
            return g.user.id
        except Exception as e:
            return None


    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return as_unicode(self.id)

    def get_full_name(self):
        return u'{0} {1}'.format(self.first_name, self.last_name)

    def __repr__(self):
        return self.get_full_name()


