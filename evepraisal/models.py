import datetime
import decimal

from . import db


# Access levels
NORMAL_USER = 0
ADMIN = 1
SUPERUSER = 2


class Scans(db.Model):
    __tablename__ = 'Scans'

    Id = db.Column(db.Integer(), primary_key=True)
    Data = db.Column(db.Text())
    Created = db.Column(db.Integer())
    SellValue = db.Column(db.Float())
    BuyValue = db.Column(db.Float())
    Public = db.Column(db.Boolean(), default=True)
    UserId = db.Column(db.Integer(), db.ForeignKey('Users.Id'))


class Users(db.Model):
    __tablename__ = 'Users'

    Id = db.Column(db.Integer(), primary_key=True)
    OpenId = db.Column(db.String(200))
    Options = db.Column(db.Text())
    AccessLevel = db.Column(db.Integer(), default=0)

    def is_superuser(self):
        return self.AccessLevel == SUPERUSER

    def is_admin(self):
        return self.AccessLevel >= ADMIN


class Modifiers(db.Model):
    """Modifiers defined by admins to affect the price of specific types"""
    __tablename__ = 'Modifiers'

    Id = db.Column(db.Integer(), primary_key=True)
    TypeId = db.Column(db.Integer(), unique=True)
    TypeName = db.Column(db.Text())
    Modifier = db.Column(db.Numeric(), default=1.0)
    CreatedBy = db.Column(db.Integer(), db.ForeignKey('Users.Id'))
    Created = db.Column(db.DateTime(), default=datetime.datetime.utcnow())


    def modify(self, pdata):
        """Modify the pricing data of an EveType"""
        if 'sell' in pdata:
            self._modify_section(pdata['sell'])
        if 'buy' in pdata:
            self._modify_section(pdata['buy'])
        if 'all' in pdata:
            self._modify_section(pdata['all'])
        return pdata

    def _modify_section(self, section):
        if not section:
            return
        for k in ['avg', 'min', 'max', 'price']:
            section[k] = float(decimal.Decimal(section[k]) * self.Modifier)

    @staticmethod
    def by_typeid(mods):
        """Returns a dictionary of typeid -> Modifier"""
        mod_dict = {}
        for m in mods:
            mod_dict[m.TypeId] = m
        return mod_dict


class EveType(object):
    def __init__(self, type_id, count=0, props=None, pricing_info=None):
        self.type_id = type_id

        self.count = count
        self.fitted_count = 0

        self.props = props or {}
        self.pricing_info = pricing_info or {}
        self.market = self.props.get('market', False)
        self.volume = self.props.get('volume', 0)
        self.type_name = self.props.get('typeName', 0)
        self.group_id = self.props.get('groupID')
        self.modifier = None

    def representative_value(self):
        if not self.pricing_info:
            return 0
        sell_price = self.pricing_info.get('totals', {}).get('sell', 0)
        buy_price = self.pricing_info.get('totals', {}).get('buy', 0)
        return max(sell_price, buy_price)

    def is_market_item(self):
        if self.props.get('market', False):
            return True
        else:
            return False

    def incr_count(self, count, fitted=False):
        self.count += count
        if fitted:
            self.fitted_count += count

    def to_dict(self):
        return {
            'typeID': self.type_id,
            'count': self.count,
            'fitted_count': self.fitted_count,
            'market': self.market,
            'volume': self.volume,
            'typeName': self.type_name,
            'groupID': self.group_id,
            'modified': self.modifier is not None,
            'totals': self.pricing_info.get('totals'),
            'sell': self.pricing_info.get('sell'),
            'buy': self.pricing_info.get('buy'),
            'all': self.pricing_info.get('all'),
        }

    @classmethod
    def from_dict(self, cls, d):
        return cls(d['typeID'], d['count'], {
            'typeName': d.get('typeName'),
            'groupID': d.get('groupID'),
            'volume': d.get('volume')
        }, {
            'totals': d.get('totals'),
            'sell': d.get('sell'),
            'buy': d.get('buy'),
            'all': d.get('all'),
        })
