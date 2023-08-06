from datetime import datetime

from blazeutils.helpers import diff
from blazeutils.strings import normalizews
from blazeweb.globals import ag
from blazeweb.testing import inrequest, TestApp
from datagridbwc.lib import Col, YesNo, DataGrid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, SmallInteger, DateTime, \
    UniqueConstraint, ForeignKey, String
from sqlalchemybwc import db
from werkzeug import Client, BaseResponse, create_environ

from datagridbwc_ta.model.orm import Car, Radio, Person, Email

testapp = ag.wsgi_test_app

c = Client(testapp, BaseResponse)

def setup_module():
    Email.delete_all()
    Person.delete_all()
    for x in range(1, 101):
        p = Person()
        p.firstname = 'fn%03d' % x
        p.lastname = 'ln%03d' % x
        if x < 90:
            p.createdts = datetime.now()
        db.sess.add(p)
    db.sess.commit()

class TestFunctional(object):

    def get_dg(self):
        tbl = Person.__table__
        p = DataGrid(
            db.sess.execute,
            )
        p.add_col(
            'Id',
            tbl.c.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname,
            filter_on=True
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname,
            filter_on=True
        )
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
            sort='drop-down'
        )
        p.add_col(
            'Sort Order',
            tbl.c.sortorder,
        )
        p.add_col(
            'createdts',
            Person.createdts,
            filter_on=True
        )
        return p

    @inrequest()
    def test_records(self):
        tbl = Person.__table__
        qobj = db.sess.query(tbl)
        count = qobj.count()
        assert count == 100, count

        qobj = db.sess.query(Person.id, Person.firstname)
        count = qobj.count()
        assert count == 100, count

        p = self.get_dg()

        assert p.count == 100
        records = p.records
        assert len(records) == p.count

    @inrequest()
    def test_html_table(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname', 'http://localhost'))

        expect = """<table cellpadding="0" cellspacing="0" summary="">
    <thead>
        <tr>
            <th><a href="/foo?page=1&amp;perpage=5&amp;sort=-firstname" class="sort-asc" title="currently sorting asc, click to reverse">First Name</a></th>
            <th><a href="/foo?page=1&amp;perpage=5&amp;sort=lastname" class="" title="">Last Name</a></th>
            <th>Inactive</th>
        </tr>
    </thead>
    <tbody>
        <tr class="odd">
            <td>fn001</td>
            <td>ln001</td>
            <td>no</td>
        </tr>
        <tr class="even">
            <td>fn002</td>
            <td>ln002</td>
            <td>no</td>
        </tr>
        <tr class="odd">
            <td>fn003</td>
            <td>ln003</td>
            <td>no</td>
        </tr>
        <tr class="even">
            <td>fn004</td>
            <td>ln004</td>
            <td>no</td>
        </tr>
        <tr class="odd">
            <td>fn005</td>
            <td>ln005</td>
            <td>no</td>
        </tr>
    </tbody>
</table>"""
        html = p.html_table
        assert html == expect, dodiff(html, expect)

    @inrequest()
    def test_html_table_outpu(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo', 'http://localhost'))
        assert p.html_table

    @inrequest()
    def test_html_table_desc_sort(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=-firstname', 'http://localhost'))

        expect = """<tr>
            <th><a href="/foo?page=1&amp;perpage=5&amp;sort=firstname" class="sort-desc" title="currently sorting desc, click to reverse">First Name</a></th>
            <th><a href="/foo?page=1&amp;perpage=5&amp;sort=lastname" class="" title="">Last Name</a></th>
            <th>Inactive</th>
        </tr>"""
        html = p.html_table
        assert expect in html, dodiff(html, expect)

    @inrequest()
    def test_html_filter_controls(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname&filteron=firstname&filteronop=eq&filterfor=test', 'http://localhost'))

        html = p.html_filter_controls
        expected = """<select class="datagrid-filteron" name="filteron">
            <option value="">&nbsp;</option>
            <option value="firstname" selected="selected">First Name</option>
            <option value="lastname">Last Name</option>
            <option value="createdts">createdts</option>
            </select><br />"""
        assert normalizews(expected) in normalizews(html), dodiff(html, expected)

        expected = """<select class="datagrid-filteronop" name="filteronop">
        <option value="">&nbsp;</option>
        <option value="contains">contains</option>
        <option value="eq" selected="selected">equal to</option>
        <option value="ne">not equal to</option>
        <option value="lt">less than</option>
        <option value="lte">less than or equal</option>
        <option value="gt">greater than</option>
        <option value="gte">greater than or equal</option>
    </select>"""
        assert normalizews(expected) in normalizews(html), dodiff(html, expected)

        assert '<input type="text" class="datagrid-filterfor" name="filterfor" value="test"/>' in html

    @inrequest()
    def test_html_sort_controls(self):
        p = self.get_dg()
        p.add_sort('inactive state DESC', Person.inactive, Person.state.desc())
        p.add_sort('inactive state ASC', Person.inactive, Person.state)
        p._replace_environ(create_environ('/foo?perpage=5&page=1&sort=firstname&filteron=firstname&filteronop=eq&filterfor=test', 'http://localhost'))

        expected = """<div class="datagrid-sort-controls-wrapper expand-around-floats">
    <div class="sortdd-wrapper">
        <select class="datagrid-sort" name="sortdd">
            <option value="">&nbsp;</option>
            <option value="inactiveasc">Inactive ASC</option>
            <option value="inactivedesc">Inactive DESC</option>
            <option value="inactivestatedesc">inactive state DESC</option>
            <option value="inactivestateasc">inactive state ASC</option>

        </select><br />
        <label>Sort</label>
    </div>
</div>"""
        html = p.html_sort_controls
        assert normalizews(expected) in normalizews(html), dodiff(html, expected)

    @inrequest()
    def test_no_sort_controls(self):
        tbl = Person.__table__
        p = DataGrid(
            db.sess.execute,
            )
        p.add_col(
            'Id',
            tbl.c.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname,
            filter_on=True
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname,
            filter_on=True
        )
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
        )
        p.add_col(
            'Sort Order',
            tbl.c.sortorder,
        )
        assert not p.html_sort_controls

    @inrequest()
    def test_no_filter_controls(self):
        tbl = Person.__table__
        p = DataGrid(
            db.sess.execute,
            )
        p.add_col(
            'Id',
            tbl.c.id,
            inresult=True
        )
        p.add_tablecol(
            Col('First Name'),
            tbl.c.firstname
            )
        p.add_tablecol(
            Col('Last Name'),
            Person.lastname
        )
        p.add_tablecol(
            YesNo('Inactive'),
            Person.inactive,
        )
        p.add_col(
            'Sort Order',
            tbl.c.sortorder,
        )
        assert not p.html_filter_controls

    @inrequest()
    def test_html_pager_controls_upper(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=20&page=3', 'http://localhost'))

        html = p.html_pager_controls_upper
        expected = """<select class="datagrid-pager-upper" name="page">
            <option value="1">1 of 5</option>
            <option value="2">2 of 5</option>
            <option value="3" selected="selected">3 of 5</option>
            <option value="4">4 of 5</option>
            <option value="5">5 of 5</option>

        </select>"""
        assert normalizews(expected) in normalizews(html), dodiff(html, expected)

        assert '<input type="text" class="datagrid-perpage" name="perpage" value="20"/>' in html

    @inrequest()
    def test_html_pager_controls_lower(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?perpage=20&page=3', 'http://localhost'))

        html = p.html_pager_controls_lower
        assert '<a class="pager-link-first" href="/foo?page=1&amp;perpage=20">first</a>' \
            in html
        assert '<a class="pager-link-previous" href="/foo?page=2&amp;perpage=20">previous</a>' \
            in html
        assert '<a class="pager-link-next" href="/foo?page=4&amp;perpage=20">next</a>' \
            in html
        assert '<a class="pager-link-last" href="/foo?page=5&amp;perpage=20">last</a>' \
            in html

        p._replace_environ(create_environ('/foo?perpage=20&page=1', 'http://localhost'))
        html = p.html_pager_controls_lower
        assert 'bd_firstpage.png' in html
        assert 'bd_prevpage.png' in html
        assert '<a class="pager-link-next" href="/foo?page=2&amp;perpage=20">' in html
        assert '<a class="pager-link-last" href="/foo?page=5&amp;perpage=20">' in html

        p._replace_environ(create_environ('/foo?perpage=20&page=5', 'http://localhost'))

        html = p.html_pager_controls_lower
        assert '<a class="pager-link-first" href="/foo?page=1&amp;perpage=20">first</a>' \
            in html
        assert '<a class="pager-link-previous" href="/foo?page=4&amp;perpage=20">previous</a>' \
            in html
        assert '<li class="dead">next' in html
        assert 'bd_nextpage.png' in html
        assert '<li class="dead">last' in html
        assert 'bd_lastpage.png' in html

    def test_blank_sortdd(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?sortdd=&page=1&perpage=10', 'http://localhost'))

        recstr = ''.join([str(r) for r in p.records])
        assert 'fn001' in recstr
        assert 'fn010' in recstr
        assert 'fn011' not in recstr

    def test_blank_sortdd_header_sort(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?sortdd=&page=1&perpage=10&sort=-firstname', 'http://localhost'))

        recstr = ''.join([str(r) for r in p.records])
        assert 'fn100' in recstr
        assert 'fn091' in recstr
        assert 'fn090' not in recstr

    def test_empty_sort(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?sortdd=&page=1&perpage=10&sort=', 'http://localhost'))

        recstr = ''.join([str(r) for r in p.records])
        assert 'fn001' in recstr
        assert 'fn010' in recstr
        assert 'fn011' not in recstr

    def test_timestamp_filter(self):
        p = self.get_dg()
        p._replace_environ(create_environ('/foo?filteron=createdts&filteronop=lt&filterfor=10%2F26%2F2000', 'http://localhost'))
        assert not p.records

    #def test_empty_timestamp_filter(self):
    #    p = self.get_dg()
    #    p._replace_environ(create_environ('/foo?filteron=createdts&filteronop=lt&filterfor=', 'http://localhost'))
    #    try:
    #        assert p.count == 11
    #    except:
    #        db.sess.rollback()
    #        raise

    @inrequest()
    def test_html_attributes(self):
        p = self.get_dg()
        assert p.html_everything

class TestInApp(object):
    @classmethod
    def setup_class(self):
        self.ta = TestApp(testapp)

    def test_everything(self):
        radio = Radio.add(make=u'b', model = u'b', year=2000 )
        c = Car.add(make=u'a', model = u'a', year=2008, radio_id=radio.id )
        r = self.ta.get('/dg1')
        assert '<h2>Test DataGrid1</h2>' in r
        assert '// data_grid1.js' in r, r
        assert '/* data_grid1.css */' in r, r

        # everything
        assert "div.datagrid-actions-wrapper a {" in r

        # filter_controls
        assert 'class="datagrid-filter-controls-wrapper' in r, r
        assert 'div.datagrid-filter-controls-wrapper' in r, r

        ## page_controls_lower.css in r
        assert 'ul.datagrid-pager-controls-lower-wrapper' in r
        assert '<ul class="datagrid-pager-controls-lower-wrapper">' in r

        # page_controls_upper.css in r
        assert 'div.datagrid-pager-controls-upper-wrapper' in r
        assert '<div class="datagrid-pager-controls-upper-wrapper' in r

        ## sort_controls.css
        assert 'div.datagrid-sort-controls-wrapper' in r
        assert '<div class="datagrid-sort-controls-wrapper' in r

        r = self.ta.get('/dg2')
        assert '<h2>Test DataGrid2</h2>' in r
